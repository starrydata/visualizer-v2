const d = cb_data.response.data;
let xe = [],
  ye = [],
  lab = [];
for (let i = 0; i < d.x.length; i++) {
  const xs = d.x[i],
    ys = d.y[i];
  xe.push(xs.length ? xs[xs.length - 1] : null);
  ye.push(ys.length ? ys[ys.length - 1] : null);
  lab.push(`${d.SID[i]}-${d.figure_id[i]}-${d.sample_id[i]}`);
}
return { x_end: xe, y_end: ye, label: lab };
