translate(v = [0, 0, 5.0]) {
	rotate(a = [180, 0, 0]) {
		difference() {
			translate(v = [0, 11.0, 0]) {
				cylinder(d = 38.0, h = 5.0);
			}
			translate(v = [0, 0, -0.1]) {
				hull() {
					cylinder(d = 7.5, h = 3.1);
					translate(v = [0, 15.25, 0]) {
						cylinder(d = 5.0, h = 3.1);
					}
				}
			}
			translate(v = [0, 0, -1]) {
				cylinder(d = 2.4, h = 7.0);
			}
		}
	}
}
