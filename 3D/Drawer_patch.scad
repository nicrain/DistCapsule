difference() {
	union() {
		translate(v = [0, -90.0, 0]) {
			cube(size = [20.0, 90.0, 3.6]);
		}
		translate(v = [-2.5, -90.0, 3.6]) {
			cube(size = [20.0, 5.0, 16.4]);
		}
		translate(v = [-29.75, -85.0, 3.6]) {
			cube(size = [47.25, 3.0, 16.4]);
		}
		translate(v = [-29.75, -20.0, 3.6]) {
			cube(size = [49.75, 10.0, 3.0]);
		}
		translate(v = [-29.85, -90.0, 8.6]) {
			cube(size = [10.0, 5.0, 6.4]);
		}
	}
	translate(v = [-12.5, -87.5, 10.0]) {
		rotate(a = [0, 90, 0]) {
			cylinder(d = 1.8, h = 80.0);
		}
	}
	translate(v = [27.5, -87.5, 10.0]) {
		rotate(a = [0, 180, 0]) {
			rotate(a = [0, 90, 0]) {
				cylinder(d = 1.8, h = 80.0);
			}
		}
	}
	union() {
		translate(v = [-14.5, -15.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [-24.5, -15.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -75.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -65.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -55.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -45.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -35.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -25.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
		translate(v = [10.0, -15.0, -1]) {
			cylinder(d = 4.0, h = 8.6);
		}
	}
}
