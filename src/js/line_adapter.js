const d = cb_data.response.data;
// UNIX 時間に変換
const ts = d.updated_at.map(t => new Date(t).getTime());
const mi = Math.min(...ts), ma = Math.max(...ts);
// シリーズ毎に線幅を計算（新しいほど太くなる）
const widths = ts.map(t => 0.1 + (ma > mi ? (t - mi)/(ma - mi)*0.2 : 0.1));
return { xs: d.x, ys: d.y, widths: widths };
