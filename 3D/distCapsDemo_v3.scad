$fn = 120;

union() {
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
	translate(v = [16.25, 54.25, -1.5]) {
		union() {
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
			translate(v = [0, 2.5, -20]) {
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
			}
		}
	}
}
