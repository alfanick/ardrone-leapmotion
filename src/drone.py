import libardrone
import time
import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class LeapParams:
  height_offset = 220.0
  # left right
  box_size_x = 180.0
  # up down
  box_size_y = 120.0
  # front back
  box_size_z = 120.0
  # rotation
  angle_range = 0.5

  def __init__(self):
    pass

params = LeapParams()

drone = libardrone.ARDrone()

class DroneListener(Leap.Listener):
    closed_height = -100
    flying = False

    def on_init(self, controller):
        print "Leap Initialized"

    def on_connect(self, controller):
        print "Leap Connected"

        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)

    def on_disconnect(self, controller):
        pass

    def on_exit(self, controller):
        pass

    def on_frame(self, controller):
        frame = controller.frame()

        if frame.hands.is_empty:
          self.closed_height = -100
          if self.flying == False:
            return
          self.hover()

        else:
          hand = frame.hands[0]

          if len(hand.fingers) <= 1:
            self.hand_closed(hand)
          else:
            self.hand_opened(hand)


          if self.flying == False:
            if len(hand.fingers) <= 1:
              print "%s %s" % (self.closed_height, hand.palm_position.y)
              if hand.palm_position.y - self.closed_height > 100:
                self.takeoff()
          elif self.flying == True:
            if len(hand.fingers) <= 1:
              if hand.palm_position.y - self.closed_height < -100:
                self.hover()
                self.land()
              else:
                self.hover()

            elif len(hand.fingers) == 2:
              self.rotate(hand.direction.x)

            else:
              pos = hand.palm_position
              self.reposition(pos.x, pos.y - params.height_offset, pos.z)

        pass

    def hand_closed(self, hand):
      if self.closed_height == -100:
        self.closed_height = hand.palm_position.y

    def hand_opened(self, hand):
      self.closed_height = -100

    def takeoff(self):
      drone.takeoff()
      self.flying = True
      print "Taking off!"

    def land(self):
      drone.land()
      self.flying = False
      print "Landing!!"

    # position.x - left/right
    # position.y - up/down
    # position.z - front/back
    def reposition (self, x, y, z):
      x = self.normalize(x, 1.5 * params.box_size_x)
      y = self.normalize(y, params.box_size_y)
      z = self.normalize(z, params.box_size_z)
      print "repositioning %.2f %.2f %.2f" % (x, y, z)
      drone.at(libardrone.at_pcmd, True, x, z, y, 0)

    def hover(self):
      print "hovering!"
      drone.hover()

    def rotate(self, angle):
      angle = min(angle, params.angle_range)
      angle = max(angle, -params.angle_range)
      angle = angle / float(params.angle_range)

      print "rotating %s" % angle
      drone.at(libardrone.at_pcmd, True, 0, 0, 0, angle)

    def normalize(self, val, box):
      val = 0 if abs(val) < 20 else val
      val = min(val, box)
      val = max(val, -box)
      val = val / float(box) / 20.0
      return val


if __name__ == "__main__":
    listener = DroneListener()
    controller = Leap.Controller()

    controller.add_listener(listener)

    sys.stdin.readline()

    controller.remove_listener(listener)
