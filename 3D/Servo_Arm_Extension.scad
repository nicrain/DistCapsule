translate(v = [0, 0, 4.0]) {
	rotate(a = [180, 0, 0]) {
		difference() {
			union() {
				difference() {
					translate(v = [0, 11.0, 0]) {
						cylinder(d = 38.0, h = 4.0);
					}
					translate(v = [0, 0, -0.1]) {
						hull() {
							cylinder(d = 7.5, h = 3.1);
							translate(v = [0, 16.5, 0]) {
								cylinder(d = 5.5, h = 3.1);
							}
						}
					}
				}
				translate(v = [0, 0, 2.0]) {
					cylinder(d = 4.0, h = 1.1);
				}
			}
			translate(v = [0, 0, 3.5]) {
				cylinder(d = 4.0, h = 1.0);
			}
			translate(v = [0, 0, -1]) {
				cylinder(d = 2.4, h = 6.0);
			}
		}
	}
}
