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
const ts = d.updated_at.map((t) => new Date(t).getTime());
const minT = Math.min(...ts);
const maxT = Math.max(...ts);
const widths = ts.map(t =>
  0.1 + (maxT > minT ? ((t - minT) / (maxT - minT)) * 0.2 : 0.1)
);

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
  widths: widths
};
