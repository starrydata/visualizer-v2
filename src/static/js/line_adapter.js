const d = cb_data.response.data;

// 終端点とラベルの計算
const x_end = [];
const y_end = [];
const label = [];
for (let i = 0; i < d.x.length; i++) {
  const xs = d.x[i];
  const ys = d.y[i];
  x_end.push(xs.length ? xs[xs.length - 1] : null);
  y_end.push(ys.length ? ys[ys.length - 1] : null);
  label.push(`${d.SID[i]}-${d.figure_id[i]}-${d.sample_id[i]}`);
}

// 更新日時から線幅の計算
const ts = d.updated_at.map((t) => new Date(t).getTime() / 1000 / 60);
const minT = Math.min(...ts);
const maxT = Math.max(...ts);
const widths = ts.map(t => {
  const normalized = maxT > minT ? (t - minT) / (maxT - minT) : 0;
  const k = 3;
  const exponential_normalized = maxT > minT ? (Math.exp(k * normalized) - 1) / (Math.exp(k) - 1) : 0;
  return 0.1 + exponential_normalized * 0.5;
});
const alphas = ts.map(t => {
  if (maxT <= minT) return 1;
  const t_norm = (t - minT) / (maxT - minT) + 0.1; // 0.1を足すことで、最初のものが完全に透明にならないようにする
  // 新しいものほど透明度が低くなる（目立つ）ように線形に変化
  return t_norm;
});
// 全てまとめて返す
return {
  // 元データ
  xs: d.x,
  ys: d.y,
  // ラベル用
  x_end: x_end,
  y_end: y_end,
  label: label,
  // 線幅
  widths: widths,
  alphas: alphas
};
