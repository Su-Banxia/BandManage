USE band_manage;
ALTER TABLE performance_songs
ADD UNIQUE INDEX performance_order_unique (performance_id, song_order);