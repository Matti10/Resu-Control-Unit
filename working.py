make USER_C_MODULES=/workspaces/Resu-Control-Unit/micropython-esp32-twai/src/micropython.cmake 
Use make V=1 or set BUILD_VERBOSE in your environment to increase build verbosity.
idf.py -D MICROPY_BOARD=ESP32_GENERIC -D MICROPY_BOARD_DIR="/workspaces/Resu-Control-Unit/micropython/ports/esp32/boards/ESP32_GENERIC" -DUSER_C_MODULES=/workspaces/Resu-Control-Unit/micropython-esp32-twai/src/micropython.cmake -B build-ESP32_GENERIC build || (echo -e "See \033[1;31mhttps://github.com/micropython/micropython/wiki/Build-Troubleshooting\033[0m"; false)
Executing action: all (aliases: build)
Running cmake in directory /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC
Executing "cmake -G 'Unix Makefiles' -DPYTHON_DEPS_CHECKED=1 -DPYTHON=/root/.espressif/python_env/idf5.2_py3.9_env/bin/python -DESP_PLATFORM=1 -DMICROPY_BOARD=ESP32_GENERIC -DMICROPY_BOARD_DIR=/workspaces/Resu-Control-Unit/micropython/ports/esp32/boards/ESP32_GENERIC -DUSER_C_MODULES=/workspaces/Resu-Control-Unit/micropython-esp32-twai/src/micropython.cmake -DCCACHE_ENABLE=0 /workspaces/Resu-Control-Unit/micropython/ports/esp32"...
-- IDF_TARGET not set, using default target: esp32
-- Found Git: /usr/bin/git (found version "2.30.2") 
-- The C compiler identification is GNU 13.2.0
-- The CXX compiler identification is GNU 13.2.0
-- The ASM compiler identification is GNU
-- Found assembler: /root/.espressif/tools/xtensa-esp-elf/esp-13.2.0_20230928/xtensa-esp-elf/bin/xtensa-esp32-elf-gcc
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /root/.espressif/tools/xtensa-esp-elf/esp-13.2.0_20230928/xtensa-esp-elf/bin/xtensa-esp32-elf-gcc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /root/.espressif/tools/xtensa-esp-elf/esp-13.2.0_20230928/xtensa-esp-elf/bin/xtensa-esp32-elf-g++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Building ESP-IDF components for target esp32
NOTICE: Skipping optional dependency: espressif/esp_tinyusb
NOTICE: Skipping optional dependency: espressif/esp_tinyusb
NOTICE: Skipping optional dependency: espressif/esp_tinyusb
NOTICE: Skipping optional dependency: espressif/esp_tinyusb
NOTICE: Processing 2 dependencies:
NOTICE: [1/2] espressif/mdns (1.1.0)
NOTICE: [2/2] idf (5.2.2)
NOTICE: Skipping optional dependency: espressif/esp_tinyusb
-- Project sdkconfig file /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/sdkconfig
Loading defaults file /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/sdkconfig.combined...
/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/sdkconfig.combined:104 CONFIG_ESP32_WIFI_IRAM_OPT was replaced with CONFIG_ESP_WIFI_IRAM_OPT
/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/sdkconfig.combined:105 CONFIG_ESP32_WIFI_RX_IRAM_OPT was replaced with CONFIG_ESP_WIFI_RX_IRAM_OPT
/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/sdkconfig.combined:163 CONFIG_BT_NIMBLE_TASK_STACK_SIZE was replaced with CONFIG_BT_NIMBLE_HOST_TASK_STACK_SIZE
-- Compiler supported targets: xtensa-esp-elf
-- Looking for sys/types.h
-- Looking for sys/types.h - found
-- Looking for stdint.h
-- Looking for stdint.h - found
-- Looking for stddef.h
-- Looking for stddef.h - found
-- Check size of time_t
-- Check size of time_t - done
-- Found Python3: /root/.espressif/python_env/idf5.2_py3.9_env/bin/python (found version "3.9.2") found components: Interpreter 
-- Looking for pthread.h
-- Looking for pthread.h - found
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD - Success
-- Found Threads: TRUE  
-- Performing Test C_COMPILER_SUPPORTS_WFORMAT_SIGNEDNESS
-- Performing Test C_COMPILER_SUPPORTS_WFORMAT_SIGNEDNESS - Success
-- App "micropython" version: v1.13-5136-gf187c77da-dirty
-- Adding linker script /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/esp-idf/esp_system/ld/memory.ld
-- Adding linker script /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/esp-idf/esp_system/ld/sections.ld.in
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom/esp32/ld/esp32.rom.ld
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom/esp32/ld/esp32.rom.api.ld
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom/esp32/ld/esp32.rom.libgcc.ld
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom/esp32/ld/esp32.rom.newlib-data.ld
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom/esp32/ld/esp32.rom.syscalls.ld
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom/esp32/ld/esp32.rom.newlib-funcs.ld
-- Adding linker script /workspaces/Resu-Control-Unit/esp-idf/components/soc/esp32/ld/esp32.peripherals.ld
Including User C Module(s) from /workspaces/Resu-Control-Unit/micropython-esp32-twai/src/micropython.cmake
Found User C Module(s): usermod_esp32can
-- Components: app_trace app_update bootloader bootloader_support bt cmock console cxx driver efuse esp-tls esp_adc esp_app_format esp_bootloader_format esp_coex esp_common esp_eth esp_event esp_gdbstub esp_hid esp_http_client esp_http_server esp_https_ota esp_https_server esp_hw_support esp_lcd esp_local_ctrl esp_mm esp_netif esp_netif_stack esp_partition esp_phy esp_pm esp_psram esp_ringbuf esp_rom esp_system esp_timer esp_wifi espcoredump espressif__mdns esptool_py fatfs freertos hal heap http_parser idf_test ieee802154 json log lwip main mbedtls mqtt newlib nvs_flash nvs_sec_provider openthread partition_table perfmon protobuf-c protocomm pthread sdmmc soc spi_flash spiffs tcp_transport ulp unity usb vfs wear_levelling wifi_provisioning wpa_supplicant xtensa
-- Component paths: /workspaces/Resu-Control-Unit/esp-idf/components/app_trace /workspaces/Resu-Control-Unit/esp-idf/components/app_update /workspaces/Resu-Control-Unit/esp-idf/components/bootloader /workspaces/Resu-Control-Unit/esp-idf/components/bootloader_support /workspaces/Resu-Control-Unit/esp-idf/components/bt /workspaces/Resu-Control-Unit/esp-idf/components/cmock /workspaces/Resu-Control-Unit/esp-idf/components/console /workspaces/Resu-Control-Unit/esp-idf/components/cxx /workspaces/Resu-Control-Unit/esp-idf/components/driver /workspaces/Resu-Control-Unit/esp-idf/components/efuse /workspaces/Resu-Control-Unit/esp-idf/components/esp-tls /workspaces/Resu-Control-Unit/esp-idf/components/esp_adc /workspaces/Resu-Control-Unit/esp-idf/components/esp_app_format /workspaces/Resu-Control-Unit/esp-idf/components/esp_bootloader_format /workspaces/Resu-Control-Unit/esp-idf/components/esp_coex /workspaces/Resu-Control-Unit/esp-idf/components/esp_common /workspaces/Resu-Control-Unit/esp-idf/components/esp_eth /workspaces/Resu-Control-Unit/esp-idf/components/esp_event /workspaces/Resu-Control-Unit/esp-idf/components/esp_gdbstub /workspaces/Resu-Control-Unit/esp-idf/components/esp_hid /workspaces/Resu-Control-Unit/esp-idf/components/esp_http_client /workspaces/Resu-Control-Unit/esp-idf/components/esp_http_server /workspaces/Resu-Control-Unit/esp-idf/components/esp_https_ota /workspaces/Resu-Control-Unit/esp-idf/components/esp_https_server /workspaces/Resu-Control-Unit/esp-idf/components/esp_hw_support /workspaces/Resu-Control-Unit/esp-idf/components/esp_lcd /workspaces/Resu-Control-Unit/esp-idf/components/esp_local_ctrl /workspaces/Resu-Control-Unit/esp-idf/components/esp_mm /workspaces/Resu-Control-Unit/esp-idf/components/esp_netif /workspaces/Resu-Control-Unit/esp-idf/components/esp_netif_stack /workspaces/Resu-Control-Unit/esp-idf/components/esp_partition /workspaces/Resu-Control-Unit/esp-idf/components/esp_phy /workspaces/Resu-Control-Unit/esp-idf/components/esp_pm /workspaces/Resu-Control-Unit/esp-idf/components/esp_psram /workspaces/Resu-Control-Unit/esp-idf/components/esp_ringbuf /workspaces/Resu-Control-Unit/esp-idf/components/esp_rom /workspaces/Resu-Control-Unit/esp-idf/components/esp_system /workspaces/Resu-Control-Unit/esp-idf/components/esp_timer /workspaces/Resu-Control-Unit/esp-idf/components/esp_wifi /workspaces/Resu-Control-Unit/esp-idf/components/espcoredump /workspaces/Resu-Control-Unit/micropython/ports/esp32/managed_components/espressif__mdns /workspaces/Resu-Control-Unit/esp-idf/components/esptool_py /workspaces/Resu-Control-Unit/esp-idf/components/fatfs /workspaces/Resu-Control-Unit/esp-idf/components/freertos /workspaces/Resu-Control-Unit/esp-idf/components/hal /workspaces/Resu-Control-Unit/esp-idf/components/heap /workspaces/Resu-Control-Unit/esp-idf/components/http_parser /workspaces/Resu-Control-Unit/esp-idf/components/idf_test /workspaces/Resu-Control-Unit/esp-idf/components/ieee802154 /workspaces/Resu-Control-Unit/esp-idf/components/json /workspaces/Resu-Control-Unit/esp-idf/components/log /workspaces/Resu-Control-Unit/esp-idf/components/lwip /workspaces/Resu-Control-Unit/micropython/ports/esp32/main /workspaces/Resu-Control-Unit/esp-idf/components/mbedtls /workspaces/Resu-Control-Unit/esp-idf/components/mqtt /workspaces/Resu-Control-Unit/esp-idf/components/newlib /workspaces/Resu-Control-Unit/esp-idf/components/nvs_flash /workspaces/Resu-Control-Unit/esp-idf/components/nvs_sec_provider /workspaces/Resu-Control-Unit/esp-idf/components/openthread /workspaces/Resu-Control-Unit/esp-idf/components/partition_table /workspaces/Resu-Control-Unit/esp-idf/components/perfmon /workspaces/Resu-Control-Unit/esp-idf/components/protobuf-c /workspaces/Resu-Control-Unit/esp-idf/components/protocomm /workspaces/Resu-Control-Unit/esp-idf/components/pthread /workspaces/Resu-Control-Unit/esp-idf/components/sdmmc /workspaces/Resu-Control-Unit/esp-idf/components/soc /workspaces/Resu-Control-Unit/esp-idf/components/spi_flash /workspaces/Resu-Control-Unit/esp-idf/components/spiffs /workspaces/Resu-Control-Unit/esp-idf/components/tcp_transport /workspaces/Resu-Control-Unit/esp-idf/components/ulp /workspaces/Resu-Control-Unit/esp-idf/components/unity /workspaces/Resu-Control-Unit/esp-idf/components/usb /workspaces/Resu-Control-Unit/esp-idf/components/vfs /workspaces/Resu-Control-Unit/esp-idf/components/wear_levelling /workspaces/Resu-Control-Unit/esp-idf/components/wifi_provisioning /workspaces/Resu-Control-Unit/esp-idf/components/wpa_supplicant /workspaces/Resu-Control-Unit/esp-idf/components/xtensa
-- Configuring done
-- Generating done
-- Build files have been written to: /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC
Running make in directory /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC
Executing "make -j 10 all"...
make[1]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[2]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
Scanning dependencies of target memory.ld
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
Scanning dependencies of target _project_elf_src
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
Scanning dependencies of target sections.ld.in
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
Scanning dependencies of target BUILD_VERSION_HEADER
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
[  1%] Generating project_elf_src_esp32.c
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
[  1%] Generating /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/esp-idf/esp_system/ld/memory.ld linker script...
Scanning dependencies of target partition_table_bin
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
[  1%] Generating /workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC/esp-idf/esp_system/ld/sections.ld.in linker script...
[  1%] Built target _project_elf_src
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
[  1%] Generating ../../partition_table/partition-table.bin
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
[  1%] Built target memory.ld
[  1%] Built target sections.ld.in
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
Partition table binary generated. Contents:
*******************************************************************************
# ESP-IDF Partition Table
# Name, Type, SubType, Offset, Size, Flags
nvs,data,nvs,0x9000,24K,
phy_init,data,phy,0xf000,4K,
factory,app,factory,0x10000,1984K,
vfs,data,fat,0x200000,2M,
*******************************************************************************
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
[  1%] Built target partition_table_bin
make[3]: Entering directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENERIC'
Scanning dependencies of target bootloader
make[3]: Leaving directory '/workspaces/Resu-Control-Unit/micropython/ports/esp32/build-ESP32_GENER