from solid2 import *

set_global_fn(120)

class distCaps:
    def __init__(self):
        self.width = 42
        self.rail_height = 2.5
        self.cover_thickness = 1.5
        self.caps_width = 38
        self.rail_int = self.caps_width - 2*3
        self.block_height = 5

        self.push_w = 10
        self.push_h = 36

        self.delta = .5

    def rail(self, l):
        obj = cube([self.width, l, self.block_height])

        obj -= translate([(self.width - self.rail_int - self.delta) / 2,
                          -1,
                          self.block_height - self.rail_height - self.cover_thickness])(
                    cube([self.rail_int + self.delta, l + 2, self.block_height])
                )

        obj -= translate([(self.width - self.caps_width - self.delta) / 2,
                          -1,
                          self.block_height - self.rail_height - self.cover_thickness])(
                    cube([self.caps_width + self.delta, l+2, self.rail_height])
                )
        return obj

    def end_block(self):
        return cube([self.width, 2, self.block_height])

    def demo(self, demolen):

        demo = self.rail(demolen)
        demo += translate([0,demolen+1,0])(d.rail(self.caps_width))
        demo += translate([0,demolen+self.caps_width+2,0])(d.end_block())
        return demo

    def v2(self, demolen):
        obj=self.rail(demolen)
        obj+=translate([0,demolen,0])(self.end_block())
        cyl_diam = self.caps_width + self.delta
        obj -= translate([self.width / 2,
                          demolen - cyl_diam / 2,
                          self.block_height - self.rail_height - self.cover_thickness])(
            cylinder(d=cyl_diam, h=self.rail_height+self.cover_thickness*2)
        )


        obj -= translate([self.width/2-self.push_w/2,
                          demolen - self.push_h,
                          -1])(cube([self.push_w, self.push_h, 10]))
        return obj

    def v3(self, demolen):
        obj=self.rail(demolen)
        obj+=translate([0,demolen,0])(self.end_block())
        cyl_diam = self.caps_width + self.delta
        obj -= translate([self.width / 2,
                          demolen - cyl_diam / 2,
                          self.block_height - self.rail_height - self.cover_thickness])(
            cylinder(d=cyl_diam, h=self.rail_height+self.cover_thickness*2)
        )


        obj -= translate([self.width/2-self.push_w/2,
                          demolen - self.push_h,
                          -1])(cube([self.push_w, self.push_h - self.delta * 2, 10]))
        return obj

    def v2_pusher(self):
        push_cube = cube([self.push_w - self.delta, self.push_h - self.delta, self.block_height + self.cover_thickness])
        push_cube += translate([-5-self.delta/2,0,0])(cube([self.push_w +10, self.push_h, self.cover_thickness]))
        return push_cube

    def pusher_handle_foot(self, w = None):
        if w is None:
            w = self.push_w
            z = self.cover_thickness
        else:
            z = self.cover_thickness + 0.5
        foot = translate(0, -1, -(z - self.cover_thickness)/2)(cube(w ,6 , z))
        foot -= translate(-self.delta / 2, -2, 0)(cube(w + self.delta, 2, 2)).rotateX(10)
        foot -= translate(-self.delta / 2, 4, 0)(cube(w + self.delta, 2, 2).rotateX(-10))
        return foot

    def pusher_handle(self):
        handle = cube(self.push_w ,4 , 20 + self.delta)
        handle -= translate(-self.delta/2, 1, self.block_height)(cube(self.push_w + self.delta ,self.push_w, 10))
        handle -= translate(-self.delta/2, 0.5, 0)(cube(self.push_w + self.delta ,5 , 10).rotateX(-30))
        # Foot for connecting to pusher

        handle += translateZ(20)(self.pusher_handle_foot())
        return handle

    def v3_pusher(self):
        push_cube = cube([self.push_w - self.delta, self.push_h - self.delta, self.block_height + self.cover_thickness])
        # Locking ramp for the capsule
        push_cube -= translate(-self.delta/2, -self.push_h/5, -(self.block_height + self.cover_thickness))(cube([self.push_w, self.push_h / 5, self.block_height + self.cover_thickness])).rotateX(20).translateZ(self.block_height + self.cover_thickness)
        # Base 
        push_cube += translate([-5-self.delta/2,0,0])(cube([self.push_w +10, self.push_h, self.cover_thickness]))
        # Long ramp
        push_cube -= translateY(-(self.push_h - self.delta))(cube([self.push_w, self.push_h - self.delta, self.block_height])).rotateX(-4.5).translate(-self.delta/2, self.push_h - self.delta, self.cover_thickness * 3 - self.delta)
        # Bottom slot
        push_cube -= translate(-self.delta/2, self.push_h - self.delta * 3, self.cover_thickness)(cube([self.push_w, self.delta * 3, self.cover_thickness]))
        # Bottom foot
        push_cube += translate(0, self.push_h - self.delta * 3, self.cover_thickness * 2)(cube([self.push_w - self.delta, self.delta * 2, self.cover_thickness * 2]))
        # For combining Handle
        push_cube -= translate(0, self.push_w/4, 0)(self.pusher_handle_foot(15))
        # Handle
        # push_cube += translate(0, self.push_w/4, -20)(self.pusher_handle())
        return push_cube

    def demo_v3_pusher_with_handle(self):
        demo_v3_pusher = self.v3_pusher()
        demo_v3_pusher += translate(0, self.push_w/4, -20)(self.pusher_handle())
        return demo_v3_pusher

    def position_pushv2(self, push_cube, demolen):
        return translate([self.width/2-self.push_w/2 + self.delta/2,
                          demolen - self.push_h + self.delta/2,
                          -self.cover_thickness])(push_cube)

d = distCaps()
#scad_render_to_file(d.demo(50), "distCapsDemo.scad")

demo_v2=d.v2(60)
demo_v3=d.v3(90)
push_v2=d.v2_pusher()
push_v3=d.v3_pusher()
handle=d.pusher_handle()
demo_push_v3_handle=d.demo_v3_pusher_with_handle()
demo_scene = demo_v2 + d.position_pushv2(push_v2, 60)
demo_scene_v3 = demo_v3 + d.position_pushv2(demo_push_v3_handle, 90)

scad_render_to_file(handle, "pusherHandle.scad")
#scad_render_to_file(demo_v2, "distCapsBase.scad")
scad_render_to_file(demo_v3, "distCapsBase_v3.scad")
#scad_render_to_file(push_v2, "distCapsPush.scad")
scad_render_to_file(push_v3, "distCapsPush_v3.scad")
scad_render_to_file(demo_push_v3_handle, "distCapsPushDemo_v3_handle.scad")

#scad_render_to_file(demo_scene, "distCapsDemo.scad")
scad_render_to_file(demo_scene_v3, "distCapsDemo_v3.scad")

#scad_render_to_file(d.rail(38), "distCaps.scad")
