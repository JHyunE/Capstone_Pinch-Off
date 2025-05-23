from cheetah_py import *
import time
import sys
import os
try:
    from detect import port
except:
    print("asdf")
from array import array
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def read_register(read_address, read_data):
    mode = 0
    handle = ch_open(port)

    print("Opened Cheetah device on port %d" % port)

    ch_spi_bitrate(handle, 100)
    ch_spi_configure(handle, (mode >> 1), mode & 1, CH_SPI_BITORDER_MSB, 0x0)
    ch_spi_queue_oe(handle, 1)
    ch_spi_queue_clear(handle)
    ch_spi_queue_ss(handle, 1)

    read_cmd_address = int(128 + read_address)  # single read for 64/burst read for 128

    MOSI_cmd_address = array('B', [0])
    MOSI_cmd_address[0] = read_cmd_address & 0xff
    MISO_data = array('B', [0] * read_data * 2)

    ch_spi_queue_array(handle, MOSI_cmd_address)
    ch_spi_batch_shift(handle, len(MOSI_cmd_address))

    ch_spi_queue_array(handle, MISO_data)
    result, data_in = ch_spi_batch_shift(handle, len(MISO_data))

    if result < 0:
        print(f"SPI Read Error: {result}")
        ch_spi_queue_ss(handle, 0)
        return None
    ch_spi_queue_ss(handle, 0)
    ch_close(port)
    return data_in

def keti_spi_write(handle, write_address, write_data):
    ########## b2h prescaler###################################
    data_1 = (write_data >> 8)  # MSB~1byte
    data_0 = (write_data & 0b11111111)  # LSB~1byte
    ########## parsinf###################################
    data_out_0 = int(write_address)  # address
    data_out_1 = int(data_1)  # MSB~8bits
    data_out_2 = int(data_0)  # LSB~8bits

    ##############write_setup#################################
    ch_spi_queue_oe(handle, 1)  # SPI 출력 사용 설정
    ch_spi_queue_clear(handle)  # SPI 큐 초기화
    data_out = array('B', [0 for i in range(3)])  # 3byte 배열 생성
    data_out[0] = data_out_0 & 0xff  # 주소
    data_out[1] = data_out_1 & 0xff  # 상위 바이트
    data_out[2] = data_out_2 & 0xff  # 하위 바이트
    #############write########################################
    ch_spi_queue_ss(handle, 0x1)  # 슬레이브 선택
    ch_spi_queue_array(handle, data_out)  # 데이터 전송
    ch_spi_queue_ss(handle, 0)  # 슬레이트 선택 비활성화
    ch_spi_async_submit(handle)


def write_register(address, hex_str):
    mode = 0
    handle = ch_open(port)  # port는 전역 변수로 정의되어 있어야 함
    print("Opened Cheetah device on port %d" % port)
    ch_spi_bitrate(handle, 100)
    data = int(hex_str, 16)
    keti_spi_write(handle, address, data)
    ch_close(port)




