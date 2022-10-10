#!/usr/bin/env python
import sys
import random
import struct
import pefile
import logging

def bin2hex(my_bytes, prefix='', to_upper=True):
	ret_str = ''
	for x in my_bytes:
		my_byte = ''
		if x < 16:
			my_byte += '0'
		my_byte += hex( x ).replace('0x', '')
		ret_str += prefix
		if to_upper:
			ret_str += my_byte.upper()
		else:
		 	ret_str += my_byte
	return ret_str


def find_all(st, substr, start_pos=0, accum=[]):
	ix = st.find(substr, start_pos)
	if ix == -1:
		return accum
	return find_all(st, substr, start_pos=ix + 1, accum=accum + [ix])

def ALIGN_UP(value, Aligment):
	if value % Aligment == 0:
		return value
	# return ((value / Aligment)+1)*Aligment
	# v2.7 python int / int = int, here we have float by default
	return (int(value / Aligment)+1)*Aligment



def genRndData(N):
	bytes = map( lambda i: chr(i), xrange(255))
	random.shuffle(bytes)
	bytes = bytes[:random.randint(0x40, 0xFF)]
	return ''.join(  map(lambda i: random.choice(bytes),  xrange(N)) )

def patch(FileIn='', fileData=None, FileOut=None, timestamp=None):

	if fileData:
		PE = pefile.PE(data=fileData)
	else:
		PE = pefile.PE(FileIn)

	# removed so dll can work good
	# PE.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']].Size = 0

	# set timestamp if needed
	if timestamp is not None and isinstance(timestamp, int):
		PE.FILE_HEADER.TimeDateStamp = timestamp

	# checksum
	if ( PE.OPTIONAL_HEADER.CheckSum != 0 and PE.OPTIONAL_HEADER.CheckSum != 0xFFFFFFFF ):
		PE.OPTIONAL_HEADER.CheckSum = random.randint(0, 0xFFFFFFFF) & 0xFFFFFFFF

	# DIRECTORY_ENTRY_EXPORT
	if hasattr(PE, 'DIRECTORY_ENTRY_EXPORT'):
		if 	(PE.DIRECTORY_ENTRY_EXPORT.struct.Characteristics == 0 and
			PE.DIRECTORY_ENTRY_EXPORT.struct.MajorVersion == 0 and
			PE.DIRECTORY_ENTRY_EXPORT.struct.MinorVersion == 0 and
			PE.DIRECTORY_ENTRY_EXPORT.struct.Name > 0 and
			PE.DIRECTORY_ENTRY_EXPORT.struct.Name < PE.OPTIONAL_HEADER.SizeOfImage and
			PE.DIRECTORY_ENTRY_EXPORT.struct.NumberOfFunctions > 0 and
			PE.DIRECTORY_ENTRY_EXPORT.struct.NumberOfFunctions < 0xFF):

				# PE.DIRECTORY_ENTRY_EXPORT.struct.TimeDateStamp = (PE.FILE_HEADER.TimeDateStamp + random.randint(-0x1FFF, 0x1FFF)) & 0xFFFFFFFFL
				PE.DIRECTORY_ENTRY_EXPORT.struct.TimeDateStamp = (PE.FILE_HEADER.TimeDateStamp + random.randint(-0x1FFF, 0x1FFF)) & 0xFFFFFFFF



	#section VirtualSize
	# TODO: figure out why this fails
	for s in PE.sections:
		if random.randint(0, 2) == 1:
			s.Misc_VirtualSize = ( s.Misc_VirtualSize + random.randint(0, ALIGN_UP(s.Misc_VirtualSize, PE.OPTIONAL_HEADER.SectionAlignment) - s.Misc_VirtualSize ) ) & 0xFFFFFFFF

	#
	#	find place for patch
	#
	#	sign  = {0xe4b0e37c, 0xabe33915, 0xC0DEC0DE}
	#	struct _PATCHED_AREA{
	# 		DWORD sign[3];
	# 		DWORD wholeSize;	== sizeof(struct _PATCHED_AREA)
	# 		unsigned char data[SizeOfData];
	# };
	#

	sign  = [0xe4b0e37c, 0xabe33915, 0xC0DEC0DE]
	# sign_str = ''.join(map(lambda s: struct.pack('L',s), sign))
	# append ugly hack to remove extra zeores in v3 python, compared to v2
	sign_str = b''.join(map(lambda s: struct.pack('L',s), sign))
	# print(''.join(map(lambda i: hex(i)[2:], sign_str)))
	# logging.info(bin2hex(sign_str, to_upper=False))
	# print(bin2hex(sign_str, to_upper=False))

	for s in PE.sections:
		rva_start, RawSize = s.VirtualAddress, s.SizeOfRawData
		data = PE.get_data(rva_start, RawSize)
		# print(f"data type:{type(data)}, sign_str type:{type(sign_str)}")
		starts = find_all(data, sign_str)
		if len(starts) == 0:
			# logging.info( f'[{FileIn}->{FileOut}]no starts found in [{s.Name}]')
			continue

		# print( '\npatched [{1}]  at positions {0}'.format(starts, s.Name))
		# logging.info( f'\npatched [{s.Name}]  at positions {starts}')
		for pos in starts:
			wholeSize = struct.unpack( 'L', data[ pos + 12:pos + 16 ] )[0]
			if wholeSize > 0xFFFF:
				# print( 'maybe someting wrong, patched size is too big. wholeSize = 0x{0:x}'.format(wholeSize) )
				# logging.info( f'[{FileIn}->{FileOut}]maybe someting wrong, patched size is too big. wholeSize = 0x{0:x}'.format(wholeSize) )
				quit(-1)
			PE.set_bytes_at_rva( rva_start + pos, genRndData(wholeSize) )
			# print('patched at {0:x}  size {1:x} '.format(rva_start + pos, wholeSize))
			# logging.info('[{2}->{3}]patched at {0:x}  size {1:x} '.format(rva_start + pos, wholeSize, FileIn, FileOut))

	# removed so dll can work good
	# PE.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']].Size = 0

	if FileOut:
		PE.write(FileOut)
		return None
	else:
		return PE.write()


def main(argv):
	patch(argv[0],argv[1])

if __name__ == '__main__':
	main(sys.argv[1:])
