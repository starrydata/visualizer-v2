const d = cb_data.response.data;
let xf = [],
  yf = [],
  sidf = [],
  sizef = [],
  line_sizef = [];
const ts = [];
for (let i = 0; i < d.x.length; i++) {
  const t = new Date(d.updated_at[i]).getTime();
  for (let j = 0; j < d.x[i].length; j++) {
    xf.push(d.x[i][j]);
    yf.push(d.y[i][j]);
    sidf.push(d.SID[i]);
    ts.push(t);
  }
}
const mi = Math.min(...ts),
  ma = Math.max(...ts);
ts.forEach((t) => sizef.push(ma > mi ? 2 + ((t - mi) / (ma - mi)) * 4 : 2));
ts.forEach((t) =>
  line_sizef.push(ma > mi ? 0.1 + ((t - mi) / (ma - mi)) * 0.4 : 0.1)
);
return { x: xf, y: yf, SID: sidf, size: sizef, line_size: line_sizef };
