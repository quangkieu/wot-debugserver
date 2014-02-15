write_client = None

import socket
g_sock = None

PORT = 2222

def run_repl():
    global write_client
    global g_sock

    newline = '\r\n'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(1)

    def repl(filestream, once=False):
        global write_client

        def echo(s):
            filestream.write(str(s))
            filestream.write(newline)
            filestream.flush()
        write_client = echo
        def doc(o):
            for line in o.__doc__.splitlines():
                echo(line)

        local_vars = {'echo': echo, 'doc': doc}

        for line in filestream:
            line = line.strip()
            #print 'line:', line
            if line == 'QUIT':
                break
            try:
                if len(line) > 2:
                    if line[0:2] == 'p ':
                        res = eval(line[2:].strip(), globals(), local_vars)
                        filestream.write(repr(res) + '\r\n')
                        filestream.flush()
                    else:
                        exec line in globals(), local_vars
            except Exception, e:
                import traceback
                echo(traceback.format_exc())
            locs = local_vars.get('__READYMSG', None)
            if locs is not None:
                echo(locs)
            if once:
                break

    try:
        conn, addr = s.accept()
        g_sock = conn
        f = conn.makefile()
        repl(f)
    except Exception, e:
        print e
        import traceback
        traceback.print_stack()
    write_client = None
    conn.close()
    s.close()

def closesocket():
    if g_sock is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', PORT))
        s.send('QUIT\r\n')
        s.close()

if __name__ == '__main__':
    print 'run repl..'
    run_repl()
