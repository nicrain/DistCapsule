$fn = 120;

difference() {
	union() {
		difference() {
			cube(size = [42, 90, 5]);
			translate(v = [4.75, -1, 1.0]) {
				cube(size = [32.5, 92, 5]);
			}
			translate(v = [1.75, -1, 1.0]) {
				cube(size = [38.5, 92, 2.5]);
			}
		}
		translate(v = [0, 90, 0]) {
			cube(size = [42, 2, 5]);
		}
	}
	translate(v = [21.0, 70.75, 1.0]) {
		cylinder(d = 38.5, h = 5.5);
	}
	translate(v = [16.0, 54, -1]) {
		cube(size = [10, 35.0, 10]);
	}
}
