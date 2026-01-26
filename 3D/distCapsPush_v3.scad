$fn = 120;

difference() {
	union() {
		difference() {
			union() {
				difference() {
					cube(size = [9.5, 35.5, 6.5]);
					translate(v = [0, 0, 6.5]) {
						rotate(a = [20, 0, 0]) {
							translate(v = [-0.25, -7.2, -6.5]) {
								cube(size = [10, 7.2, 6.5]);
							}
						}
					}
				}
				translate(v = [-5.25, 0, 0]) {
					cube(size = [20, 36, 1.5]);
				}
			}
			translate(v = [-0.25, 35.5, 4.0]) {
				rotate(a = [-4.5, 0, 0]) {
					translate(v = [0, -35.5, 0]) {
						cube(size = [10, 35.5, 5]);
					}
				}
			}
			translate(v = [-0.25, 34.5, 1.5]) {
				cube(size = [10, 1.5, 1.5]);
			}
		}
		translate(v = [0, 34.5, 3.0]) {
			cube(size = [9.5, 1.0, 3.0]);
		}
	}
	translate(v = [0, 2.5, 0]) {
		difference() {
			translate(v = [0, -1, -0.25]) {
				cube(size = [15, 6, 2.0]);
			}
			rotate(a = [10, 0, 0]) {
				translate(v = [-0.25, -2, 0]) {
					cube(size = [15.5, 2, 2]);
				}
			}
			translate(v = [-0.25, 4, 0]) {
				rotate(a = [-10, 0, 0]) {
					cube(size = [15.5, 2, 2]);
				}
			}
		}
	}
}
