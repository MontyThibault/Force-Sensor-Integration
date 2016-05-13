import PAIO

def main():
	device = PAIO.AIODevice()
	aio = PAIO.AIO()

	device.Init()
	device.AioSetAiRangeAll(aio.PM10)

if __name__ == "__main__":
	main()