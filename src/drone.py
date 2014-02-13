import libardrone
import time
import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class LeapParams:
  front_offset = 30.0
  height_offset = 220.0
  # left right
  box_size_x = 160.0
  # up down
  box_size_y = 120.0
  # front back
  box_size_z = 100.0
  # rotation
  angle_range = 0.4

  scale_x = 100.0
  scale_y = 100.0
  scale_z = 100.0

  last_flip_wait_time = 1.5

  def __init__(self):
    pass

params = LeapParams()

drone = libardrone.ARDrone()

class DroneListener(Leap.Listener):
    closed_height = -100
    flying = False

    def on_init(self, controller):
        print "Leap Initialized"
        self.start_time = time.time()
        self.last_flip_time = time.time() - 10

    def on_connect(self, controller):
        print "Leap Connected"

        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)

        controller.config.set("Gesture.Circle.MinRadius", 100.0)
        #controller.config.set("Gesture.Circle.MinArc", 6)

        controller.config.save()

    def on_disconnect(self, controller):
        pass

    def on_exit(self, controller):
        pass

    def on_frame(self, controller):
        if time.time() - self.last_flip_time < params.last_flip_wait_time:
          return

        # Prevent leap from reading unnecessary stuff
        if time.time() - self.start_time < 1.5:
          return

        frame = controller.frame()


        for gesture in frame.gestures():
          if self.flying == True and gesture.type == Leap.Gesture.TYPE_CIRCLE:
            circle = CircleGesture(gesture)
            if circle.normal.z > 0.8:
              self.flip_it_baby_left()
            if circle.normal.z < -0.8:
              self.flip_it_baby_right()
            return

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
              #pos = hand.palm_position
              #self.rotate_with_reposition(hand.direction.x, pos.x, 0, pos.z - params.front_offset)

            else:
              pos = hand.palm_position
              self.reposition(pos.x, pos.y - params.height_offset, pos.z - params.front_offset)
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
      x = self.normalize(x, params.box_size_x, params.scale_x)
      y = self.normalize(y, params.box_size_y, params.scale_y)
      z = self.normalize(z, params.box_size_z, params.scale_z)
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

    def rotate_with_reposition(self, angle, x, y, z):
      angle = min(angle, params.angle_range)
      angle = max(angle, -params.angle_range)
      angle = angle / float(params.angle_range)

      x = self.normalize(x, params.box_size_x, params.scale_x)
      y = self.normalize(y, params.box_size_y, params.scale_y)
      z = self.normalize(z, params.box_size_z, params.scale_z)

      print "rotating %s + movement(%.2f %.2f %.2f)" % (angle, x, y, z)
      drone.at(libardrone.at_pcmd, True, x, z, y, angle)


    def normalize(self, val, box, scale):
      val = 0 if abs(val) < 20 else val
      val = min(val, box)
      val = max(val, -box)
      val = val / float(box) * scale / 100.0
      return val

    def flip_it_baby_left(self):
      self.last_flip_time = time.time()
      print "FLAAAAAAAPPING BIIIIRD! (left)"
      drone.at(libardrone.at_anim, 18, 800)

    def flip_it_baby_right(self):
      self.last_flip_time = time.time()
      print "FLAAAAAAAPPING BIIIIRD! (right)"
      drone.at(libardrone.at_anim, 19, 800)


if __name__ == "__main__":
    """
    drone.land()
    time.sleep(2)

    print "startuje"

    drone.takeoff()
    time.sleep(8)

    print "tanczy"
    drone.at(libardrone.at_anim, 18, 1000)

    time.sleep(5)

    print "laduje"
    drone.hover()

    drone.land()
    """

    listener = DroneListener()
    controller = Leap.Controller()

    controller.add_listener(listener)

    sys.stdin.readline()

    controller.remove_listener(listener)
