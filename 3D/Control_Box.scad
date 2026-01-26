difference() {
	cube(size = [100.0, 50.0, 200.0]);
	translate(v = [3.0, 3.0, 3.0]) {
		cube(size = [94.0, 50.0, 194.0]);
	}
	translate(v = [38.5, -5, 7.0]) {
		cube(size = [23.0, 13.0, 46.0]);
	}
	translate(v = [38.0, -5, 88.0]) {
		cube(size = [24.0, 13.0, 24.0]);
	}
	translate(v = [50.0, -5, 180.0]) {
		rotate(a = [-90, 0, 0]) {
			cylinder(d = 8.0, h = 13.0);
		}
	}
	translate(v = [-5, 6, 50]) {
		rotate(a = [0, 90, 0]) {
			cylinder(d = 3.2, h = 13.0);
		}
	}
	translate(v = [-5, 6, 100]) {
		rotate(a = [0, 90, 0]) {
			cylinder(d = 3.2, h = 13.0);
		}
	}
	translate(v = [-5, 6, 150]) {
		rotate(a = [0, 90, 0]) {
			cylinder(d = 3.2, h = 13.0);
		}
	}
	translate(v = [-5, 15, 120]) {
		cube(size = [13.0, 20, 40]);
	}
	translate(v = [95.0, 15, 120]) {
		cube(size = [13.0, 20, 40]);
	}
	rotate(a = [15.0, 0, 0]) {
		translate(v = [-10, -10, -50]) {
			cube(size = [120.0, 100.0, 50]);
		}
	}
}
