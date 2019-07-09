import argparse, glob, os, sys
from pythonvideoannotator_models.models import Project
from .idtrackerai_importer import import_idtrackerai_project

def progress(count, max_count, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(max_count)))

    percents = round(100.0 * count / float(max_count), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def run():
    parser = argparse.ArgumentParser(
        description='Crawl all the subdirectories searching for idtrackerai '
                    'projects and convert them to Python Video Annotator projects.')

    parser.add_argument('path', type=str,
                        help='Path where to search for idtrackerai projects')


    args = parser.parse_args()

    print("SEARCHING FOR IDTRACKERAI PROJECTS INSIDE THE DIRECTORY:", args.path)

    for blobs_path in glob.glob( os.path.join(args.path, '**', 'preprocessing', 'blobs_collection*.npy'), recursive=True):

        path = os.path.dirname(os.path.dirname(blobs_path))

        vidobj_path = os.path.join(path, 'video_object.npy')

        if os.path.exists(blobs_path) and os.path.exists(vidobj_path):
            print()
            print('IMPORTING THE PROJECT:', path)

            proj = Project()
            import_idtrackerai_project(proj, path, progress_event=progress)

            annotator_projpath = os.path.join(path, 'video-annotator-proj')
            os.mkdir( annotator_projpath )
            proj.save({},annotator_projpath)


if __name__ == '__main__': run()