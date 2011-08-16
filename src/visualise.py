import random
import sys

SECS_PER_PX = 0.5
ZOOM = 5.0

greenlets = {}
free_x = []
max_x = 0

start_timestamp = None
end_timestamp = 0

def format_greenlet(greenlet):
    colour = '#' + ''.join([random.choice('0123456789ab') for r in range(6)])
    print '<div onclick="console.log(\'Args: %s\\nStack: %s\')" style="position: absolute; left: %spx; top: %spx; height: %spx; width: %spx; border: 1px solid white; background-color: %s"> </div>' % (
        greenlet['args'].replace("'", "\\'"),
        greenlet['stack'].replace("<", "\\x3c").replace(">", "\\x3e").replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\x22').replace("\\\\n", "\\n"),
        greenlet['x'] * 3 * ZOOM,
        ZOOM * (greenlet['start'] - start_timestamp) / SECS_PER_PX,
        ZOOM * max(1, (greenlet['end'] - greenlet['start']) / SECS_PER_PX) - 2,
        3 * ZOOM - 2,
        colour,
    )

def next_line():
    return sys.stdin.readline().strip()

while True:
    # Read a chunk
    chunk_type = next_line()
    if chunk_type == '':
        break

    _id = next_line()

    timestamp = next_line()
    timestamp = float(timestamp)

    if chunk_type == 'C':
        stack = next_line()

        if not start_timestamp:
            start_timestamp = timestamp

        if free_x:
            x = free_x.pop(0)
        else:
            x = max_x
            max_x += 1

        greenlets[_id] = {'start': timestamp, 'x': x, 'stack': stack}
    elif chunk_type == 'S':
        args = next_line()
        greenlets[_id]['args'] = args
    else:
        greenlet = greenlets[_id]
        greenlet['end'] = timestamp
        format_greenlet(greenlet)
        del(greenlets[_id])
        free_x.append(greenlet['x'])
    end_timestamp = max(end_timestamp, timestamp)


for greenlet in greenlets.values():
    greenlet['end'] = end_timestamp
    format_greenlet(greenlet)
