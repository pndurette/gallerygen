import os, sys, shutil, json, pystache
import PIL
from PIL import Image

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR = os.path.join(CUR_DIR, "templates")
CONTENTS_DIR = os.path.join(CUR_DIR, "contents")
DESTINATION_DIR = os.path.join(CUR_DIR, "html")

META_FILE = "meta.json"
IMAGES_DIR = "img"
THUMBNAIL_DIR = "thumbs"
THUMBNAIL_WIDTH = 280
FULL_WIDTH = 800

def render_page(data, template, destination):
    """ Generic-ish function to render a page """
    try:
        renderer = pystache.Renderer(search_dirs=TEMPLATE_DIR)
        with open(destination, 'w') as f:
            f.write(renderer.render_name(template, data))
    except Exception as e:
        pass

def gen_image(source, destination, width):
    img = Image.open(source)
    wpercent = (width/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((width,hsize), PIL.Image.ANTIALIAS)
    img.save(destination)

def get_images_from(path):
    """ Return list of images filenames in directory `path` """
    IMG_EXT = [".jpg", ".jpeg", ".gif", ".png"]
    try:
        # Filter out extensions that are not in IMG_EXT
        filenames = os.listdir(path)
        return filter(lambda f: os.path.splitext(f)[1].lower() in IMG_EXT, filenames)
    except Exception: raise

def main():
    # Clear dest dir
    if os.path.exists(DESTINATION_DIR):
        shutil.rmtree(DESTINATION_DIR)

    # Create new dest dir
    os.makedirs(DESTINATION_DIR)

    # All data
    contents = {}

    # Load main metadata
    try:
        with open(os.path.join(CONTENTS_DIR, META_FILE)) as meta_file:
            main_data = json.load(meta_file)
            contents.update(main_data)
    except Exception as e:
        print(e)
        sys.exit(1)

    # Load items metadata
    items = []
    pages = os.walk(CONTENTS_DIR).next()[1]
    for p in pages:
        try:
            with open(os.path.join(CONTENTS_DIR, p, META_FILE)) as meta_file:
                page_data = json.load(meta_file)
                page_data['images'] = get_images_from(os.path.join(CONTENTS_DIR, p))
                page_data['name'] = p
                if page_data['thumb'] not in page_data['images']:
                    error = "'Thumbnail image '%s' does not exist. Check metadata." % page_data['thumb']
                    raise Exception(error)
                
                # To reference the images in the template
                page_data['fullimage_path'] = os.path.join(p, IMAGES_DIR)
                page_data['thumbnail_path'] = os.path.join(p, IMAGES_DIR, THUMBNAIL_DIR)
                
                items.append(page_data)
        except Exception as e: print(e)
    contents["items"] = items

    # Index page
    print("Processing %s.." % "Index")
    render_page(contents, "index", os.path.join(DESTINATION_DIR, "index.html"))
    
    # Items pages
    for i in contents['items']:
        print("Processing %s.." % i['title'])

        # Make directories
        item_dir = os.path.join(DESTINATION_DIR, i['name'])
        images_dir = os.path.join(DESTINATION_DIR, i['fullimage_path'])
        thumbs_dir = os.path.join(DESTINATION_DIR, i['thumbnail_path'])
        os.makedirs(item_dir)
        os.makedirs(images_dir)
        os.makedirs(thumbs_dir)

        # Create item page
        render_page(i, "item", os.path.join(item_dir, "index.html"))

        # Create images
        for img in i['images']:
            source_dir = os.path.join(CONTENTS_DIR, i['name'], img)
            gen_image(source_dir, os.path.join(images_dir, img), FULL_WIDTH)
            gen_image(source_dir, os.path.join(thumbs_dir, img), THUMBNAIL_WIDTH)

if __name__ == "__main__":
    main()
