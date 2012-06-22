import MySQLdb
import sys
import server
import time
from deploy_worker import deploy_worker

con = None

try:
	conn = MySQLdb.connect( host="localhost", db="gitdeploy", user="gitdeploy", passwd="xxx" )
	cursor = conn.cursor( MySQLdb.cursors.DictCursor )
	cursor.connection.autocommit(True)

	while 1:
		time.sleep(1)

		cursor.execute("SELECT COUNT(*) FROM `queue` WHERE `pulled` = 0;")
		if(cursor.fetchone()["COUNT(*)"] > 0):
			cursor.execute("SELECT * FROM `queue` LEFT JOIN `deployments` ON `deployments`.`id` = `queue`.`deployment_id` LEFT JOIN `servers` ON `deployments`.`server_id` = `servers`.`id`")

			for queue_item in cursor.fetchall():
				deploy_worker(queue_item["host"], int(queue_item["port"]), queue_item["servers.username"], queue_item["path"], queue_item["username"], queue_item["repo"], queue_item["branch"]).start()
				cursor.execute("UPDATE `queue` SET `pulled` = 1 WHERE `id` = '%s'" % queue_item["id"])

except Exception as ex:
		print "Error: %s" % ex.__str__()

finally:

		if con:
				con.close()
