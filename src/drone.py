import libardrone
import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


class DroneListener(Leap.Listener):
    def on_init(self, controller):
        print "Leap Initialized"

    def on_connect(self, controller):
        print "Leap Connected"

        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        pass

    def on_exit(self, controller):
        pass

    def on_frame(self, controller):
        print "yay"
        pass

if __name__ == "__main__":
    listener = DroneListener()
    controller = Leap.Controller()

    controller.add_listener(listener)

    print "foo"

    sys.stdin.readline()

    controller.remove_listener(listener)

