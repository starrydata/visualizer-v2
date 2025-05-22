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
ts.forEach((t) => {
  const normalized = ma > mi ? (t - mi) / (ma - mi) : 0;
  const k = 3;
  const exponential_normalized = ma > mi ? (Math.exp(k * normalized) - 1) / (Math.exp(k) - 1) : 0;
  sizef.push(ma > mi ? 2 + exponential_normalized * 8 : 10);
});
ts.forEach((t) => {
  const normalized = ma > mi ? (t - mi) / (ma - mi) : 0;
  const k = 3;
  const exponential_normalized = ma > mi ? (Math.exp(k * normalized) - 1) / (Math.exp(k) - 1) : 0;
  line_sizef.push(ma > mi ? 0.1 + exponential_normalized * 0.4 : 0.5);
});
return { x: xf, y: yf, SID: sidf, size: sizef, line_size: line_sizef };
