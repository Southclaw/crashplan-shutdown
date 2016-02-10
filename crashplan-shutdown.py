import subprocess
import time
import datetime
import re
import tailer


TIME_INTERVAL = 600


# I 02/09/16 03:07AM [CORSAC Backup] Completed backup to F:/Backup/ in 3 hours: 71,822 files (159.50GB) backed up, 140.90GB encrypted and sent @ 153.4Mbps (Effective rate: 199.8Mbps)
# I 02/09/16 11:41AM [CORSAC Backup] Completed backup to F:/Backup/ in < 1 minute: 4 files (1KB) backed up, 0MB encrypted and sent
re_record = re.compile(r'I ([0-9/: APM]*) (\[.* Backup\]) Completed backup to (.*) in (.*): (.*) files (.*) backed up, (.*) encrypted and sent( @ (.*) \(Effective rate: (.*)\))?')
re_datetime = re.compile(r'([0-9]*)/([0-9]*)/([0-9]*) ([0-9]*):([0-9]*)[AP]M')


def deferred_check():

	# Get the last 3 lines of the file
	s = tailer.tail(open('C:\\ProgramData\\CrashPlan\\log\\history.log.0'), 3)

	log = []
	tmp = []

	for i, l in enumerate(s):
		tmp = re_record.match(l)
		if tmp:
			log = tmp

	if log == -1:
		return False

	# log is now the latest log line for a complete backup
	# check if it was in the last ~5 minutes
	# 02/09/16 11:41AM

	timedata = re_datetime.match(log.group(1))

	nowtime = datetime.datetime.now()
	logtime = datetime.datetime(
		int("20" + timedata.group(3)),	# year
		int(timedata.group(1)),			# day   damn silly month/day mixup
		int(timedata.group(2)),			# month
		int(timedata.group(4)),			# hour
		int(timedata.group(5)),			# minute
		tzinfo = nowtime.tzinfo)

	diff = (nowtime-logtime).seconds
	print("log time:", logtime)
	print("now time:", nowtime)

	# was the latest completed backup was in the last 10 minutes?
	if diff < TIME_INTERVAL:
		print("Backup completed " + str(diff) + " seconds ago. Shutting down...")
		subprocess.call(["shutdown", "/s", "/t", "60"])
		return True

	print("Fail: Last backup was", diff, "seconds ago, greater than", TIME_INTERVAL, "seconds ago.")

	return False


def main():

	while(True):

		if(deferred_check()):
			break

		time.sleep(300)


if __name__ == '__main__':
	main()
