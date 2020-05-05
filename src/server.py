import asyncio
import json
import time
import datetime
from enum import Enum
import logging
from scrapy.crawler import CrawlerProcess, logger
import glob
import os
from Crawlers.XSMN.XSMN.spiders.sxmt import SxmtSpider
from Crawlers.XSMN.XSMN.spiders.xsmb import SxmbSpider
from Crawlers.XSMN.XSMN.spiders.xsmn import SxmnSpider
from utils import *

port = 5000
host = "127.0.0.1"

clients = dict()

logging.addLevelName(1, __name__)
logger = logging.getLogger(__name__)

time_pointer = datetime.date(2020, 1, 1)


def update_data():
    today = datetime.datetime.today()
    xsmn_process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': './Data/xsmn.json'
    })
    xsmn_process.crawl(SxmnSpider)
    xsmb_process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': './Data/xsmb.json'
    })
    xsmb_process.crawl(SxmbSpider)
    xsmt_process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': './Data/xsmt.json'
    })
    xsmt_process.crawl(SxmtSpider)
    xsmn_process.start()
    time.sleep(0.1)
    xsmb_process.start()
    time.sleep(0.1)
    xsmt_process.start()
    time.sleep(0.1)


def clean_stuff():
    xsmn_process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': './Data/xsmn.json'
    })
    xsmn_process.crawl(SxmnSpider)
    xsmb_process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': './Data/xsmb.json'
    })
    xsmb_process.crawl(SxmbSpider)
    xsmt_process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': './Data/xsmt.json'
    })
    xsmt_process.crawl(SxmtSpider)
    xsmn_process.stop()
    time.sleep(0.1)
    xsmb_process.stop()
    time.sleep(0.1)
    xsmt_process.stop()
    time.sleep(0.1)


async def show_tasks():
    """FOR DEBUGGING"""
    while True:
        await asyncio.sleep(5)
        logger.debug(asyncio.Task.all_tasks())


def parse(data):
    if not data:
        return STATE.ERROR, ["", ""]
    data = data.decode("utf8")
    query = data.strip().split()
    if not query:
        return STATE.ERROR, query
    if len(query) == 1:
        query.append("")
        if query[0] == 'h':
            return STATE.HELP, query
        else:
            return STATE.INDEPENDENCE, query
    if len(query) == 2:
        query[0] = convert(query[0])
        return STATE.AUTORESULT, query
    return STATE.ERROR, query


def client_connected_cb(client_reader, client_writer):
    # Use client's port as client ID
    client_id = client_writer.get_extra_info('peername')

    logger.info('Client connected: {}'.format(client_id))

    # Define the clean up function here
    def client_cleanup(fu):
        logger.info('Cleaning up client {}'.format(client_id))
        try:  # Retrievre the result and ignore whatever returned, since it's just cleaning
            fu.result()
        except Exception as e:
            pass
        # Remove the client from client records
        del clients[client_id]

    task = asyncio.ensure_future(client_task(client_reader, client_writer))
    task.add_done_callback(client_cleanup)
    # Add the client and the task to client records
    clients[client_id] = task


async def client_task(reader, writer):
    client_addr = writer.get_extra_info('peername')
    logger.info('Start connection to {}'.format(client_addr))
    writer.write("Hello {0}\n"
                 "This is a welcome message from lottery result server\n"
                 "Please sent h or --help for more information\n".format(client_addr).encode('utf8'))
    await writer.drain()
    while True:
        data = await reader.read(1024)
        if data == b'quit\r\n':
            logger.info('Received EOF. Client disconnected.')
            writer.close()
            await writer.wait_closed()
            return
        else:
            state, query = parse(data)
            state, rev = query_handler(state, query[0], query[1])

            res = json.dumps(rev)
            res = str(state.value) + res
            logger.info('Sent packet to client...')
            writer.write(res.encode('utf8'))
            await writer.drain()  # Flow control, see later


async def main(host, port):
    global time_pointer
    now = datetime.datetime.now()
    # Clean old data
    if now.date() > time_pointer:
        for file in glob.glob("./Data/*.json"):
            os.remove(file)
        logger.info("START CRAWLING ...")
        # Clean old connection
        clean_stuff()
        update_data()
        time.sleep(1)
        # Clean stuff for next update! WARNING, plz dont remove
        clean_stuff()
        time.sleep(1)
        time_pointer = now.date()
        logger.info("CRAWLING DONE")
    # Bind server up
    read_data()
    server = await asyncio.start_server(client_connected_cb, host, port)

    logger.info(f"Server has been bind at {host}:{port}")
    await server.serve_forever()


try:
    asyncio.run(main(host, port))
except KeyboardInterrupt:
    print("Server has been shutting down..")
    time.sleep(1)
