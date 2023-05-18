# Image morphing from scratch
## 1. About this project
Image morphing is an interesting technique in Image Processing which can produce a smooth transition between two objects by stacking frames of "mean" object in increasing timesteps. The "mean" object is the half-way mapping of a region in the image with the associating region in another image and the percentage of transition is defined using the timestep variable, typically in [0, 1]. In this project, I am trying to create a transition between human faces by applying exactly the technique.
## 2. Main technique
### 2.1. Image warping
Image warping refers to the transformation of a spatial property of a region in the image. Some basic operations are translation, rotation, scaling, shearing and the combination of them. These operations can be represented by a transformation matrix T whose size depends on the specific operation. Image warping is utilized to create the transition between two associating regions in different images.
### 2.2. Color cross-dissolving
Not only the shape must be intermediated, but the color too! Color cross-dissolving is doing the same with image warping. It applies the timestep variable to the intermediate pixel intensity, which is the combination of two corresponding pixels from two different images.
## 3. Algorithm
1. Find desired corresponding regions between two images by specify the face landmark points.
2. Triangulate the two images using those points for corresponding regions. This can be achieve using various triangulation algorithm. The one I am using is Delaunay triangulation algorithm.
3. Create in-between frames by finding intermidiate image using image warping and color cross-dissolving on every corresponding regions at different timesteps
4. Combining all the frames to create the seamless transition.
## 4. Result
This is a small .GIF file to illustrate the transition between 3 faces. In the result, there is still pepper noise and I am planning to remove it using filters or interpolation in the future.

![Alt Text](result.gif)

Have fun!

Nam Ha
