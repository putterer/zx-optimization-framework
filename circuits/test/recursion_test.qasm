OPENQASM 2.0;
include "../qelib1.inc";

gate g1(p) q {
    rz(p) q;
}

gate g2(p) b {
    g1((p - 2) * 40) b;
}

gate g3(test) s {
    g2((test / 40) + 2) s;
}

gate g4(p) q {
    g3(sqrt(p)) q;
}

gate g5(jjh) tt {
    g4(jjh^2) tt;
}

qreg q[2];
creg c[1];

g5(pi * 0.5) q[1];

measure q[1] -> c[0];