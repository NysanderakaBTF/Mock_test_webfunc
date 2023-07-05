from unittest import TestCase, mock
import aiohttp

async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock") 
    async with aiohttp.ClientSession(connector=conn) as session: 
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1")as resp: 
            async for line in resp.content: 
                print(name, line)

class LogsTest(TestCase):
    async def test_logs(self):
        captured_output = []

        def mock_print(*args, **kwargs):
            captured_output.append(' '.join(str(arg) for arg in args))

        async def handler(request):
            response = aiohttp.web.StreamResponse()
            response.content_type = 'text/plain'
            await response.prepare(request)
            await response.write(b'line1\n')
            await response.write(b'line2\n')
            await response.write(b'line3\n')
            return response
        app = aiohttp.web.Application()
        app.router.add_get('/containers/{cont}/logs', handler)
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, 'localhost', 8080)
        await site.start()

        with mock.patch('builtins.print', side_effect=mock_print):
            cont = 'container_id'
            name = 'container_name'
            await logs(cont, name)

        await runner.cleanup()
        expected_output = [
            'container_name line1',
            'container_name line2',
            'container_name line3'
        ]
        self.assertEqual(captured_output, expected_output)


