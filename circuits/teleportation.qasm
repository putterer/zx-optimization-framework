qreg source[1];
qreg entangled[2];
creg c0[1];
creg c1[1];
creg target[1];
qreg zero[1];

// entangled pair preparation
h entangled[0];
cx entangled[0],entangled[1];

barrier source[0], entangled[0], entangled[1];

// prepare source state
rx(1.92) source[0];
barrier source[0], entangled[0], entangled[1];


// teleport source
cx source[0], entangled[0];
h source[0];

measure source[0] -> c0[0];
measure entangled[0] -> c1[0];

barrier source[0], entangled[0], entangled[1];

// transmit classical bits
if(c1==1) x entangled[1];
if(c0==1) z entangled[1];

// reset classical registers
measure zero[0] -> c0[0];
measure zero[0] -> c1[0];

barrier source[0], entangled[0], entangled[1], zero[0];

measure entangled[1] -> target[0];