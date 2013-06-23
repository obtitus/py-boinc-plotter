from socket import socket

class Boinccmd(socket):
    def __init__(self, addr='', portNr=31416, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.previous_data = ''
        self.addr = addr
        self.portNr = portNr
    
    def __enter__(self):
        self.connect((self.addr, self.portNr))
        return self
    def __exit__(self, type, value, traceback):
        self.close()

    def request(self, command):
        buf = "<boinc_gui_rpc_request>\n"\
               "<%s/>\n"\
               "</boinc_gui_rpc_request>\n\003"\
               % (command)
        #print 'BUF', buf
        self.sendall(buf)
        return self.recv_end()

    def recv_end(self):
        """ Iterator over lines of self.recv()
        """
        End = '\003'
        more_data = True
        while more_data:
            data = self.previous_data + self.recv(4096) # previous data gets included
            data = data.split('\n')
            self.previous_data = ''

            for line_ix in xrange(len(data)): # For each line
                if End in data[line_ix]:
                    more_data = False # breaks outer loop
                    break             # breaks inner loop
                elif line_ix == len(data)-1: # no endmark and last line
                    self.previous_data = data[line_ix]
                else:
                    yield data[line_ix]

            ix = data[line_ix].find(End) # yield until End mark
            if ix != -1:
                yield data[line_ix][:ix]
                self.previous_data += data[line_ix][:ix]

        
with Boinccmd() as s:
    for line in s.request('get_state'):
        print line
    #print s.request('get_simple_gui_info')
    #print s.request('get_results')
