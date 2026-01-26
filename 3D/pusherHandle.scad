$fn = 120;

union() {
	difference() {
		cube(size = [10, 4, 20.5]);
		translate(v = [-0.25, 1, 5]) {
			cube(size = [10.5, 10, 10]);
		}
		translate(v = [-0.25, 0.5, 0]) {
			rotate(a = [-30, 0, 0]) {
				cube(size = [10.5, 5, 10]);
			}
		}
	}
	translate(v = [0, 0, 20]) {
		difference() {
			translate(v = [0, -1, -0.0]) {
				cube(size = [10, 6, 1.5]);
			}
			rotate(a = [10, 0, 0]) {
				translate(v = [-0.25, -2, 0]) {
					cube(size = [10.5, 2, 2]);
				}
			}
			translate(v = [-0.25, 4, 0]) {
				rotate(a = [-10, 0, 0]) {
					cube(size = [10.5, 2, 2]);
				}
			}
		}
	}
}
