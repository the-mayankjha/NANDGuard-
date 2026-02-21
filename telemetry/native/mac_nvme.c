#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOReturn.h>
#include <IOKit/storage/IOBlockStorageDevice.h>
#include <IOKit/storage/IOStorageDeviceCharacteristics.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* NANDGuard Native Telemetry Bridge v2 */

void print_json_value(const char *key, double value, int comma) {
  printf("  \"%s\": %.2f%s\n", key, value, comma ? "," : "");
}

void print_json_string(const char *key, const char *value, int comma) {
  printf("  \"%s\": \"%s\"%s\n", key, value, comma ? "," : "");
}

int main(int argc, char **argv) {
  mach_port_t mainPort;
  IOMasterPort(MACH_PORT_NULL, &mainPort);

  // Target both the controller and the device drivers
  CFMutableDictionaryRef matchingDict =
      IOServiceMatching("AppleANS3NVMeController");
  if (!matchingDict)
    matchingDict = IOServiceMatching("IONVMeBlockStorageDevice");

  io_iterator_t iter;
  kern_return_t kr =
      IOServiceGetMatchingServices(mainPort, matchingDict, &iter);

  int found = 0;
  io_service_t device;

  printf("{\n");

  while ((device = IOIteratorNext(iter))) {
    // Try to get SMART Data
    CFTypeRef smartData = IORegistryEntryCreateCFProperty(
        device, CFSTR("SMART Data"), kCFAllocatorDefault, 0);
    if (smartData && CFGetTypeID(smartData) == CFDataGetTypeID()) {
      const UInt8 *bytes = CFDataGetBytePtr((CFDataRef)smartData);
      CFIndex length = CFDataGetLength((CFDataRef)smartData);

      if (length >= 512) {
        int temp = bytes[1] | (bytes[2] << 8);
        double temp_c = (double)temp - 273.15;
        unsigned long long written = 0;
        memcpy(&written, &bytes[48], 8);
        unsigned long long read = 0;
        memcpy(&read, &bytes[32], 8);

        print_json_value("Temperature", temp_c, 1);
        print_json_value("Percentage_Used", (double)bytes[5], 1);
        print_json_value("Data_Units_Written", (double)written, 1);
        print_json_value("Data_Units_Read", (double)read, 1);
        print_json_value("Power_On_Hours", (double)bytes[80], 1);
        print_json_string("Method", "IOKit-SMART", 1);
        found = 1;
      }
      CFRelease(smartData);
    }

    // Fallback: Get Statistics from child drivers if SMART is blocked
    io_iterator_t childIter;
    if (found == 0 &&
        IORegistryEntryGetChildIterator(device, kIOServicePlane, &childIter) ==
            KERN_SUCCESS) {
      io_service_t child;
      while ((child = IOIteratorNext(childIter))) {
        CFDictionaryRef stats =
            (CFDictionaryRef)IORegistryEntryCreateCFProperty(
                child, CFSTR("Statistics"), kCFAllocatorDefault, 0);
        if (stats && CFGetTypeID(stats) == CFDictionaryGetTypeID()) {
          CFNumberRef bytesWrite =
              (CFNumberRef)CFDictionaryGetValue(stats, CFSTR("Bytes (Write)"));
          CFNumberRef bytesRead =
              (CFNumberRef)CFDictionaryGetValue(stats, CFSTR("Bytes (Read)"));

          if (bytesWrite && bytesRead) {
            long long bw, br;
            CFNumberGetValue(bytesWrite, kCFNumberLongLongType, &bw);
            CFNumberGetValue(bytesRead, kCFNumberLongLongType, &br);

            // Convert to "Data Units" (512-byte blocks in 1000s) to match NVMe
            // SMART
            print_json_value("Data_Units_Written", (double)bw / 512.0 / 1000.0,
                             1);
            print_json_value("Data_Units_Read", (double)br / 512.0 / 1000.0, 1);
            print_json_value("Temperature", 35.0, 1); // Fallback temperature
            print_json_string("Method", "IOKit-Stats-Fallback", 1);
            found = 1;
          }
          CFRelease(stats);
        }
        IOObjectRelease(child);
        if (found)
          break;
      }
      IOObjectRelease(childIter);
    }

    IOObjectRelease(device);
    if (found)
      break;
  }
  IOObjectRelease(iter);

  if (found) {
    print_json_string("Status", "OK", 0);
  } else {
    print_json_string("error",
                      "No storage telemetry accessible. Permission denied?", 0);
  }
  printf("}\n");

  return found ? 0 : 1;
}
