function refine_points(img_file, pts_file, newfig)

I = im2double(imread(img_file));
pts = load_points(pts_file);

h = fspecial('log', [5, 5], 0.25);
%h = fspecial('laplacian', 0.5);
%Ig = imgaussfilt(I, 1.5);
%Ie = imfilter(rgb2gray(Ig), h);

Ihsv = rgb2hsv(I);
Ihsv(:,:,3) = 1.0;
Ig = hsv2rgb(Ihsv);

Ie = imgradient(rgb2gray(Ig));
%Ie = imfilter(rgb2gray(Ig), h);

if newfig
    fig = figure; 
else
    clf;
end

boundary_points = 1:15;

subplot(1, 5, 1); imshow(I); axis equal; hold on; plot(pts(:,1), pts(:,2), 'g.');
subplot(1, 5, 2); imshow(Ie); hold on; 

% compute the adjustment vector for each boundary point
for i=1:14
    v{i} = pts(i+1,:) - pts(i,:);
    n{i} = [-v{i}(2), v{i}(1)];
    n{i} = n{i} / norm(n{i});
    % plot the normal direction
    if false
        mp = 0.5 * (pts(i+1,:) + pts(i,:));
        vec = [mp - n{i} * 10; mp; mp + n{i} * 10];
        plot(vec(:,1), vec(:,2), 'b-', 'linewidth', 2);
    end
end

nvec = zeros(15, 2);
nvec(1,:) = n{1};
vec = [pts(1,:) - n{1} * 10; pts(1,:); pts(1,:) + n{1} * 10];
plot(vec(1:2,1), vec(1:2,2), 'g-', 'linewidth', 2);
plot(vec(2:3,1), vec(2:3,2), 'b-', 'linewidth', 2);
for i=2:14
    np = n{i-1};
    nn = n{i};
    dp = norm(pts(i-1,:) - pts(i,:));
    dn = norm(pts(i+1,:) - pts(i,:));
    ni = (dp * np + dn * nn) / (dp + dn);
    ni = ni / norm(ni);
    nvec(i,:) = ni;
    vec = [pts(i,:) - ni * 10; pts(i,:); pts(i,:) + ni * 10];
    plot(vec(1:2,1), vec(1:2,2), 'g-', 'linewidth', 2);    
    plot(vec(2:3,1), vec(2:3,2), 'b-', 'linewidth', 2);    
end
nvec(15,:) = n{end};
vec = [pts(15,:) - n{end} * 10; pts(15,:); pts(15,:) + n{end} * 10];
plot(vec(1:2,1), vec(1:2,2), 'g-', 'linewidth', 2);
plot(vec(2:3,1), vec(2:3,2), 'b-', 'linewidth', 2);

plot(pts(:,1), pts(:,2), 'g.'); plot(pts(boundary_points,1), pts(boundary_points,2), 'r.');

% now plot the samples
plot_curves = false;
pts0 = pts;
curvs0 = compute_curvatures(pts0(1:15,:), nvec);

for iters=1:3
    
    % compute the adjustment vector for each boundary point
    nvec = compute_normal_vectors(pts);
    
    % curveture constaints
    curv = compute_curvatures(pts(1:15,:), nvec);
    
    % find the target points for point constraints
    if plot_curves
        figure;
    end
    for i=1:15
        m = pts(i,:);
        ni = nvec(i,:);
        mp = m - ni * 10/(2^iters);
        mn = m + ni * 10/(2^iters);
        vals = sample_image(Ie, mp, mn, 20);
        
        p = polyfit(1:20, vals', 2);
        
        % find the peaks, and pick the best as candidate
        [max_val, max_loc] = max(vals);
        
        new_points(i,:) = mp + (mn - mp) / 20 * max_loc;
        new_points(i,:) = 0.5 * (new_points(i,:) + m);
        
        if plot_curves
            subplot(8, 2, i); hold on; plot(1:20, vals, '-b'); plot(1:20, polyval(p, 1:20), '-r');
            title(['point ', num2str(i)]);
        end
    end
    
    % find optimal points
    % target points are new points
    fun = @(x) cost_func(x, pts(1:15, :), new_points, curv);
    x0 = ones(15, 1) * 0.5;
    x = fmincon(fun, x0, [], [], [], [], zeros(15, 1), 1.5*ones(15, 1))
    
    for j=1:15
        pts(j,:) = new_points(j,:) * x(j) + (1-x(j)) * pts(j,:);
    end
    
    figure(fig);
    subplot(1, 5, 2+iters); imshow(I); hold on; plot(pts0(:,1), pts0(:,2), 'g.'); plot(pts(boundary_points,1), pts(boundary_points,2), 'r.');
end

end

function f = cost_func(x, orig_pts, target_pts, curvs)

pts = zeros(15, 2);
for i=1:15
    pts(i,:) = x(i) * target_pts(i,:) + (1-x(i)) * orig_pts(i,:);
end

w_dist = 1.0;
c1 = (x-1).*(x-1) * w_dist;

w_curv = 10.0;

nvec = compute_normal_vectors(pts);
curvs_i = compute_curvatures(pts, nvec);
c2 = sum((curvs - curvs_i).^2 * 100.0, 2) * w_curv;

norm(c1)
norm(c2)

f = norm(c1 + c2);
end

function nvec = compute_normal_vectors(pts)
    for i=1:14
        v{i} = pts(i+1,:) - pts(i,:);
        n{i} = [-v{i}(2), v{i}(1)];
        n{i} = n{i} / norm(n{i});
    end

    nvec = zeros(15,2);
    nvec(1,:) = n{1};
    for i=2:14
        np = n{i-1};
        nn = n{i};
        dp = norm(pts(i-1,:) - pts(i,:));
        dn = norm(pts(i+1,:) - pts(i,:));
        ni = (dp * np + dn * nn) / (dp + dn);
        ni = ni / norm(ni);
        nvec(i,:) = ni;
    end
    nvec(15,:) = n{end};
end

function curv = compute_curvatures(pts, nvec)
size(pts)
size(nvec)
curv = zeros(size(pts));
for i=2:size(pts,1)-1
    dnp = nvec(i,:) - nvec(i-1,:);
    dnn = nvec(i+1,:) - nvec(i,:);
    dp = norm(pts(i-1,:) - pts(i,:));
    dn = norm(pts(i+1,:) - pts(i,:));
    curv(i,:) = (dp * dnp + dn * dnn) / (dp + dn);
end
end

function v = bilinear_sample(I, p)
pul = floor(p);
pbr = ceil(p);

xl = pul(1); xr = pbr(1);
yu = pul(2); yb = pbr(2);

vul = I(yu, xl, :);
vur = I(yu, xr, :);
vbl = I(yb, xl, :);
vbr = I(yb, xr, :);

f = p - pul;
g = 1 - f;
v =   g(1) * g(2) * vul ...
    + g(1) * f(2) * vbl ...
    + f(1) * f(2) * vbr ...
    + f(1) * g(2) * vur;

v = v(:);
end

function vals = sample_image(I, p0, p1, steps)
v = p1 - p0;
dv = v / steps;

p = p0;
vals = [];
for i=1:steps
    pi = bilinear_sample(I, p);
    vals = [vals; sum(pi)];
    p = p + dv;
end

end

function pts = load_points(filename)
fid = fopen(filename, 'r');
n = fscanf(fid, '%d', 1);
pts = fscanf(fid, '%f', n*2);
pts = reshape(pts, 2, [])';
fclose(fid);
end
