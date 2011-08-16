import random
import sys

SECS_PER_PX = 0.5
ZOOM = 3.0

greenlets = {}
colours = {}
free_x = []
max_x = 0
max_concurrent = 0

start_timestamp = None
end_timestamp = 0

start_colours = [
    '#ff0000',
    '#00ff00',
    '#0000ff',
    '#880000',
    '#008800',
    '#000088',
    '#ff8800',
    '#ff00ff',
    '#00ffff',
    '#000000',
    '#888888',
]

def sanitise(string):
    return string.replace("<", "\\x3c").replace(">", "\\x3e").replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\x22').replace("\\\\n", "\\n")

def format_greenlet(greenlet):
    if greenlet['fn'] in colours:
        colour = colours[greenlet['fn']]
    else:
        if start_colours:
            colour = start_colours.pop(0)
        else:
            colour = '#' + ''.join([random.choice('0123456789ab') for r in range(6)])
        colours[greenlet['fn']] = colour
    print '<div onclick="console.log(\'Fn: %s\\nLength: %ss\\nArgs: %s\\nStack: %s\')" style="position: absolute; left: %spx; top: %spx; height: %spx; width: %spx; border: 1px solid white; background-color: %s"> </div>' % (
        sanitise(str(greenlet['fn'])),
        sanitise(str(greenlet['end'] - greenlet['start'])),
        sanitise(greenlet['args']),
        sanitise(greenlet['stack']),
        greenlet['x'] * 3 * ZOOM,
        ZOOM * (greenlet['start'] - start_timestamp) / SECS_PER_PX,
        ZOOM * max(1, (greenlet['end'] - greenlet['start']) / SECS_PER_PX) - 2,
        3 * ZOOM - 2,
        colour,
    )

line_num = 0
def next_line():
    global line_num
    line_num += 1
    return sys.stdin.readline().strip()

try:
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
            args = args.split(',')
            fn = args[0]
            args = ','.join(args[1:])
            greenlets[_id]['fn'] = fn
            greenlets[_id]['args'] = args
        else:
            greenlet = greenlets[_id]
            greenlet['end'] = timestamp
            format_greenlet(greenlet)
            del(greenlets[_id])
            free_x.append(greenlet['x'])
        end_timestamp = max(end_timestamp, timestamp)
        max_concurrent = max(max_concurrent, len(greenlets))
except:
    sys.stderr.write('Failed at line %d\n' % line_num)
    raise

for greenlet in greenlets.values():
    greenlet['end'] = end_timestamp + (end_timestamp - start_timestamp)
    if 'args' not in greenlet:
        greenlet['args'] = ''
    if 'fn' not in greenlet:
        greenlet['fn'] = ''
    format_greenlet(greenlet)

print '<div style="position: absolute; right: 100px; top: 0px; width: 150px; height: 100px;">%d concurrent eventlets</div>' % max_concurrent

print '<div style="position: absolute; left: 0px; top: %spx; height: 3px; width: %spx; border: 1px solid white; background-color: black"> </div>' % (
    ZOOM * (greenlet['start'] - start_timestamp) / SECS_PER_PX,
    ZOOM * max_x * 3,
) 
