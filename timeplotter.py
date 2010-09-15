import Image, ImageDraw
import datetime

class TimePlotter(object):
    width = 640
    @property
    def height(self):
        return sum(slot.height for slot in self.slots)

    def __init__(self):
        self.slots = []

    def plot(self, show=True):
        self.im = Image.new("RGBA", (self.width, self.height), color="white")
        draw_obj = ImageDraw.Draw(self.im)
        y0 = 0

        for slot in self.slots:
            slot.draw(draw_obj, y0)
            y0 += slot.height

    def save(self, file):
        self.im.save(file)

class Slot(object):
    def __init__(self, name):
        self.name = name
        self.times = []

    width = TimePlotter.width
    height = 50

    NAME_X = 40
    LB = 140
    RB = 600
    MID = height/2

    HOUR_PLACES = [0, 3, 6, 9, 12, 15, 18, 21, 24]

    SCALE_HEIGHT = 3

    CIRCLE_RADIUS = 3
    SPIKE_HEIGHT = 5

    def time_to_x(self, t):
        return self.seconds_to_x(t.hour*3600 + t.minute*60 + t.second)

    def seconds_to_x(self, s):
        return self.LB + (self.RB - self.LB) * (s) / 86400

    def draw(self, draw_obj, y0):
        mid = y0 + self.MID
        draw_obj.text([self.NAME_X,mid], self.name, fill="black")
        draw_obj.line([self.LB,mid,self.RB,mid], fill="blue")

        for h in self.HOUR_PLACES:
            x = self.seconds_to_x(h*3600)
            draw_obj.line([x,mid, x,mid-self.SCALE_HEIGHT], fill="blue")
            draw_obj.text([x,mid], "%02d:00"%h, fill="black")

        for t in self.times:
            x = self.time_to_x(t)
#            draw_obj.ellipse([x-self.CIRCLE_RADIUS, mid-self.CIRCLE_RADIUS,
#                x+self.CIRCLE_RADIUS, mid+self.CIRCLE_RADIUS],
#                outline="black", fill="red")

            draw_obj.line([x, mid-self.SPIKE_HEIGHT, x, mid+self.SPIKE_HEIGHT],
                    fill="red")

def plot_user_times(user_times, filename):
    """ user_times: A list of tuples containing the username and a list of times
        user_times :: [(username, [time, ...]), ...]
        """
    tp = TimePlotter()
    for un,times in user_times:
        slot = Slot(un)
        slot.times.extend(times)
        tp.slots.append(slot)
    tp.plot()
    tp.save(filename)

def plot_user_times_by_thread_list(thread_list, filename, min_sup = None):
    """ thread_list: The data generated by dumpboard.py
        Use dumpboard.load_pickle to get the thread_list.
        """

    import re
    time_pat = re.compile(r"(\d+):(\d+):(\d+)")
    people_times = {}
    for tid,ps in thread_list:
        for p in ps:
            username = p['username']
            hour,minute,second = map(int,time_pat.findall(p['date'])[0])
            t = datetime.time(hour,minute,second)
            people_times.setdefault(username,[]).append(t)

    user_times = sorted(people_times.items(),
            key=lambda(k,v):len(v), reverse=True)

    if min_sup is not None:
        user_times = [(k,v) for (k,v) in user_times if len(v) > min_sup]

    plot_user_times(user_times, filename)
