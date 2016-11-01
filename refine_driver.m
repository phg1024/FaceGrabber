for i = 1:100
    
img_filename = sprintf('/home/phg/Storage/Data/InternetRecon2/Andy_Lau/crop/%d.jpg', i);
pts_filename = sprintf('/home/phg/Storage/Data/InternetRecon2/Andy_Lau/crop/%d.pts', i);

refine_points(img_filename, pts_filename, true);
pause;
end