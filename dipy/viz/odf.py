import numpy as np
from enthought.mayavi import mlab

def disp_odf(sph_map, theta_res=64, phi_res=32, colormap='RGB', colors=256):
    import Image

    pi = np.pi
    sin = np.sin
    cos = np.cos

    theta, phi = np.mgrid[0:2*pi:theta_res*1j, 0:pi:phi_res*1j] 
    x = sin(phi)*cos(theta)
    y = sin(phi)*sin(theta)
    z = cos(phi)
    
    nvox = np.prod(sph_map.dim)

    x_cen, y_cen, z_cen = _3grid(sph_map.dim)
    
    odf_values = sph_map.evaluate_at(theta, phi)
    max_value = odf_values.max()

    mlab.figure()
    for ii in range(nvox):
        odf_ii = odf_values.reshape(nvox, theta_res, phi_res)[ii,:,:]
        odf_ii /= max_value * 2
        if colormap == 'RGB':
            rgb = np.r_['-1,3,0', x*odf_ii, y*odf_ii, z*odf_ii]
            rgb = np.abs(rgb*255/rgb.max()).astype('uint8')
            odf_im = Image.fromarray(rgb, mode='RGB')
            odf_im = odf_im.convert('P', palette=Image.ADAPTIVE, colors=colors)
            
            lut = np.empty((colors,4),'uint8')
            lut[:,3] = 255
            lut[:,0:3] = np.reshape(odf_im.getpalette(),(colors,3))

            oo = mlab.mesh(x*odf_ii + x_cen.flat[ii], 
                           y*odf_ii + y_cen.flat[ii], 
                           z*odf_ii + z_cen.flat[ii], 
                           scalars=np.int16(odf_im))
            oo.module_manager.scalar_lut_manager.lut.table=lut
        else:
            oo = mlab.mesh(x*odf_ii + x_cen.flat[ii], 
                           y*odf_ii + y_cen.flat[ii], 
                           z*odf_ii + z_cen.flat[ii], 
                           scalars=odf_ii,
                           colormap=colormap)

def _3grid(dim):

    if len(dim) > 3:
        raise ValueError('cannot display 4d image')
    elif len(dim) < 3:
        d = [1, 1, 1]
        d[0:len(dim)] = dim
    else:
        d = dim
    
    return np.mgrid[0:d[0], 0:d[1], 0:d[2]]

if __name__ == '__main__':
    import dipy.core.qball as qball
    filename='/Users/bagrata/HARDI/E1322S8I1.nii.gz'
    grad_table_filename='/Users/bagrata/HARDI/E1322S8I1.bvec'
    from nipy import load_image, save_image

    grad_table, b_values = qball.read_bvec_file(grad_table_filename)
    img = load_image(filename)
    print 'input dimensions: '
    print img.ndim
    print 'image size: '
    print img.shape
    print 'image affine: '
    print img.affine
    print 'images has pixels with size: '
    print np.dot(img.affine, np.eye(img.ndim+1)).diagonal()[0:3]
    data = np.asarray(img)

    theta, phi = np.mgrid[0:2*np.pi:64*1j, 0:np.pi:32*1j]
    odf_i = qball.odf(data[188:192,188:192,22:24,:],4,grad_table,b_values)
    disp_odf(odf_i)
