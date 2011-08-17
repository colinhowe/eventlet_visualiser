import random
import sys


def sanitise(string):
    '''Sanitises the given string so that it can be output in javascript.
    Escaped newlines are handled so that they will be output as newlines
    in a string.
    Note: This could do a much better job...
    '''
    return string.replace("<", "\\x3c").replace(">", "\\x3e").replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\x22').replace("\\\\n", "\\n")


class Visualiser(object):
    '''This is the main class that does all the work.
    '''
    # Stuff to tweak
    SECS_PER_PX = 0.5 # How many seconds per pixel on the y-axis
    ZOOM = 5.0 # A multiplier for all output 

    # Randomising colours is fine... but choosing the first few from a few stock
    # ones helps prevent colours being too close together. Plus it looks better
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
        '#88ff00',
        '#8800ff',
        '#0088ff',
        '#00ff88',
    ]

    colours = {} # Map of functions to colours
    free_x = [] # points on the x-axis currently unused
    max_x = 0 # Maximum width seen so far

    greenlets = {} # Greenlets currently being processed
    start_timestamp = None # Earliest timestamp
    end_timestamp = 0 # Oldest timestamp

    line_num = 0 # Tracks what line number we're at - for error reporting

    def next_line(self):
        '''Gets the next line in the input.
        '''
        self.line_num += 1
        return sys.stdin.readline().strip()

    def go(self):
        try:
            while self.read_chunk(): pass
        except:
            sys.stderr.write('Failed at line %d\n' % self.line_num)
            raise
        
        # Any greenlets that are left by this stage have not terminated by program end
        # Assign a time to them that is twice as long as the time elapsed so far so
        # that they stand out
        # Their args and function must also be set to blank so they can be output
        for greenlet in self.greenlets.values():
            greenlet['end'] = self.end_timestamp + (self.end_timestamp - self.start_timestamp)
            if 'args' not in greenlet:
                greenlet['args'] = ''
            if 'fn' not in greenlet:
                greenlet['fn'] = ''
            self.format_greenlet(greenlet)

        print '<div style="position: absolute; right: 100px; top: 0px; width: 150px; height: 100px;">%d concurrent eventlets</div>' % self.max_x

        # Print out a horizontal bar across the page to mark where the program ended
        print '<div style="position: absolute; left: 0px; top: %spx; height: 3px; width: %spx; border: 1px solid white; background-color: black"> </div>' % (
            self.ZOOM * (self.end_timestamp - self.start_timestamp) / self.SECS_PER_PX,
            self.ZOOM * self.max_x * 3,
        ) 

    def read_chunk(self):
        '''Reads a chunk and stores it in greenlets. If no chunk was found
        then returns None. Otherwise, returns the greenlet.
        '''
        chunk_type = self.next_line()
        if chunk_type == '':
            return None

        _id = self.next_line()

        timestamp = float(self.next_line())

        if not self.start_timestamp:
            self.start_timestamp = timestamp
        self.end_timestamp = max(self.end_timestamp, timestamp)

        if chunk_type == 'C':
            # Chunk indicates the creation of a greenthread
            stack = self.next_line()

            # free_x tracks the slots on the x-axis that are free
            # If no slots are free then we increment the maximum x value
            if self.free_x:
                x = self.free_x.pop(0)
            else:
                x = self.max_x
                self.max_x += 1

            greenlet = {'start': timestamp, 'x': x, 'stack': stack}
            self.greenlets[_id] = greenlet

        elif chunk_type == 'S':
            # Chunk indicates the start of processing of a greenthread
            args = self.next_line()
            fn, args = args.split(',', 1)

            greenlet = self.greenlets[_id]
            greenlet['fn'] = fn
            greenlet['args'] = args

        else:
            # Chunk must be the end of a greenthread
            greenlet = self.greenlets[_id]
            greenlet['end'] = timestamp
            
            del(self.greenlets[_id])
            self.free_x.append(greenlet['x'])

            self.format_greenlet(greenlet)

        return greenlet

    def format_greenlet(self, greenlet):
        # Group greenlets by colour using the function they are calling
        if greenlet['fn'] in self.colours:
            colour = self.colours[greenlet['fn']]
        else:
            if self.start_colours:
                colour = self.start_colours.pop(0)
            else:
                colour = '#' + ''.join([random.choice('0123456789ab') for r in range(6)])
            self.colours[greenlet['fn']] = colour

        fn = sanitise(str(greenlet['fn']))
        duration = str(greenlet['end'] - greenlet['start'])
        args = sanitise(greenlet['args'])
        stack = sanitise(greenlet['stack'])
        left = greenlet['x'] * 3 * self.ZOOM
        top = self.ZOOM * (greenlet['start'] - self.start_timestamp) / self.SECS_PER_PX
        height = self.ZOOM * max(1, (greenlet['end'] - greenlet['start']) / self.SECS_PER_PX) - 2
        width = 3 * self.ZOOM - 2

        print '<div onclick="console.log(\'Fn: {fn}\\nLength: {duration}s\\nArgs: {args}\\nStack: {stack}\')" style="position: absolute; left: {left}px; top: {top}px; height: {height}px; width: {width}px; border: 1px solid white; background-color: {colour}"> </div>'.format(**locals())

Visualiser().go()
