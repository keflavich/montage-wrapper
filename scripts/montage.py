#!/usr/bin/env python
import optparse
import os,shutil
import glob
import tempfile
import time

# hack because montage.py will self-import...
# there MUST be a better way to do this
import sys
for path in sys.path:
    if path[-3:] == "bin":
        sys.path.remove(path)

import montage.wrappers as mw

def wrapper(args, outfile=None, tmpdir='tmp', header='header.hdr',
        exact_size=True, combine='median', getheader=False, copy=False,
        background_match=False, tmpdrive="/var/tmp/",
        remove_tmpdir=False, hdu=None):
    """
    Usage: montage outfile=filename.fits *.fits combine=median

         Wrapper to mosaic a *subset* of images in the current directory
    Usage:     mGetHdr template_fitsfile.fit mosaic.hdr     montage
    outfile=l089_reference_montage.fits 0*_indiv13pca*_map01.fits combine=median &
    Keyword parameters:       combine - 'median', 'average', or 'sum'       header
    - Filename of fits file from which to create mosaic.hdr       outfile - Output
    fits filename

    Options:
      -h, --help            show this help message and exit
      --header=HEADER       Name of the .hdr file or a fits file from which to
                            extract a header.  Defaults to mosaic.hdr
      -g, --get-header      Get the header of the first input file?  Overrides
                            --header.  Default False
      --combine=COMBINE     How to combine the images.  Options are mean, median,
                            count.  Default median
      -X, --exact, --exact_size, --exact-size
                            Use exact_size=True?  Default True
      -o OUTFILE, --outfile=OUTFILE, --out=OUTFILE
                            Output file name
      --copy                Copy files instead of hard-linking
      --background_match    background_match images?
      --tmpdir=TMPDIR       Alternative name for temporary directory (default
                            'tmp')
      --tmpdrive=TMPDRIVE   The temporary directory in which to do coadding
                            (important that it is on the same physical HD)
      --hdu=HDUID           Which HDU to use (applies to ALL images!)
    """

    tempfile.tempdir = tmpdrive

    filelist = []
    if type(args) is str:
        raise TypeError("Args must be a list of glob expressions")
    for a in args:
        filelist += glob.glob(a)
        
    print filelist

    #echo "Creating temporary directory and sym-linking all files into it"
    print "Creating temporary directory"
    if os.path.exists(tmpdir) and remove_tmpdir:
        shutil.rmtree(tmpdir)
        os.mkdir(tmpdir+"/")
    elif not os.path.exists(tmpdir):
        os.mkdir(tmpdir+"/")
    if copy:
        print "Copying all files into %s" % tmpdir
        for fn in filelist:
            shutil.copy(fn,'%s/%s' % (tmpdir,os.path.split(fn)[-1]))
        shutil.copy(header,'%s/%s' % (tmpdir,os.path.split(header)[-1]))
    else:
        print "Hard-linking (not sym-linking) all files into %s" % tmpdir
        for fn in filelist:
            os.link(fn,'%s/%s' % (tmpdir,os.path.split(fn)[-1]))
        os.link(header,'%s/%s' % (tmpdir, os.path.split(header)[-1]))

    olddir = os.getcwd()
    print "Changing directory to %s, with old dir %s" % (tmpdir,olddir)
    os.chdir(tmpdir+'/')
    dir = os.getcwd()
    print ("Beginning montage operations: "+
            "montage.wrappers.mosaic(%s,'%s/mosaic',header='%s/%s', "+
            "exact_size=%s, combine=%s, background_match=%s)") % \
            (dir, dir, dir, options.header, options.exact, options.combine,
                    options.background_match)
    mw.mosaic(dir,'%s/mosaic' % dir,header='%s/%s' %
            (dir,os.path.split(header)[-1]), exact_size=exact_size,
            combine=combine, background_match=background_match,
            hdu=hdu)

    time.sleep(1)

    print "Changing directory back to %s" % olddir
    os.chdir(olddir)
    if os.path.exists(tmpdir+'/mosaic/mosaic.fits'):
        shutil.move(tmpdir+'/mosaic/mosaic.fits',outfile)
        print "Successfully created %s" % outfile
    else:
        print "WARNING: Did not delete %s/ because %s/mosaic/mosaic.fits was not found." % (tmpdir,tmpdir)

    shutil.rmtree(tmpdir+'/')

if __name__ == "__main__":

    parser=optparse.OptionParser()

    parser.add_option("--header",default='mosaic.hdr',help="Name of the .hdr file or a fits file from which to extract a header.  Defaults to mosaic.hdr")
    parser.add_option("--get-header","-g",default=False,action='store_true',help="Get the header of the first input file?  Overrides --header.  Default False")
    parser.add_option("--combine",default='median',help="How to combine the images.  Options are mean, median, count.  Default median")
    parser.add_option("--exact","--exact_size","--exact-size","-X",default=True,action='store_true',help="Use exact_size=True?  Default True")
    parser.add_option("--outfile","--out","-o",default=None,help="Output file name")
    parser.add_option("--copy",default=False,action='store_true',help="Copy files instead of linking")
    parser.add_option("--background_match",default=False,action='store_true',help="background_match images?")
    parser.add_option("--tmpdir",default="tmp",help="Alternative name for temporary directory (default 'tmp')")
    parser.add_option("--tmpdrive",default='/var/tmp',help="The temporary directory in which to do coadding (important that it is on the same physical HD)")
    parser.add_option("--hdu",default=None,help="Which HDU to use (applies to ALL files)")
    parser.add_option("--remove_tmpdir",default=False,help="Remove the temporary directory at the start?",action='store_true')

    parser.set_usage("%prog outfile=filename.fits *.fits combine=median")
    parser.set_description(
    """
    Wrapper to mosaic a *subset* of images in the current directory
                                                                                           
    Usage:
    mGetHdr template_fitsfile.fit mosaic.hdr
    montage outfile=l089_reference_montage.fits 0*_indiv13pca*_map01.fits combine=median &
                                                                                           
    Keyword parameters:
      combine - 'median', 'average', or 'sum'
      header  - Filename of fits file from which to create mosaic.hdr
      outfile - Output fits filename
    """)

    options,args = parser.parse_args()

    
    if options.outfile is None:
        raise ValueError("Must specify outfile name")

    hduid = int(options.hdu) if options.hdu is not None else None

    wrapper(args, outfile=options.outfile, tmpdir=options.tmpdir,
            header=options.header, exact_size=options.exact,
            combine=options.combine, getheader=options.get_header,
            copy=options.copy, background_match=options.background_match,
            tmpdrive=options.tmpdrive, remove_tmpdir=options.remove_tmpdir,
            hdu=hduid)


