#!/home/robot/.envs/reddit-video/bin/python

import praw
import gtts
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys


def read_save(text, number):
    tts = gtts.gTTS(text, lang="pt-pt")
    tts.save("audios/{:03d}_temp.mp3".format(number))
    os.system(
        'ffmpeg -i audios/{:03d}_temp.mp3 -filter:a "atempo=1.6" -vn -loglevel quiet audios/{:03d}.mp3'.format(
            number, number
        )
    )
    os.system("rm audios/{:03d}_temp.mp3".format(number))


def intro_img(author, title, description):
    font_size = 24
    width = 1920
    font_width = font_size // 1.5
    line_height = int(font_size * 1.5)

    font1 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", font_size)
    font2 = ImageFont.truetype(
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf", int(font_size * 1.5)
    )

    lines_title = textwrap.wrap(title, width=width // font_width)
    lines_title_nr = len(lines_title) + 1

    lines_description = textwrap.wrap(description, width=width // font_width)
    lines_description_nr = len(lines_description)

    image = Image.new(
        mode="RGB",
        size=(
            1760,
            lines_title_nr * int(line_height * 1.5)
            + lines_description_nr * line_height
            + 10,
        ),
        color="#1A1A1A",
    )
    draw = ImageDraw.Draw(image)
    draw.text((16, 10), author, font=font1, fill=(69, 139, 186))

    y = 10 + line_height
    for line in lines_title:
        draw.text((16, y), line, font=font2, fill="#ffffff")
        y += line_height * 1.5

    for line in lines_description:
        draw.text((16, y), line, font=font1, fill="#ffffff")
        y += line_height

    # save file
    image.save("images/000.png")


def post_img(author, text, number):
    font_size = 24
    width = 1920
    font_width = font_size // 1.5
    line_height = int(font_size * 1.5)

    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", font_size)

    lines = textwrap.wrap(text, width=width // font_width)
    lines_nr = len(lines) + 1

    image = Image.new(
        mode="RGB", size=(1760, lines_nr * line_height + 10), color="#1A1A1A"
    )
    draw = ImageDraw.Draw(image)
    draw.text((16, 10), author, font=font, fill=(69, 139, 186))

    y = 10 + line_height
    for line in lines:
        draw.text((16, y), line, font=font, fill="#ffffff")
        y += line_height

    # save file
    image.save("images/{:03d}.png".format(number))


def get_image_audio(number):
    os.system(
        "ffmpeg -loop 1 -i images/{:03d}.png -i audios/{:03d}.mp3 -c:v libx264 -tune stillimage -c:a copy -pix_fmt yuv420p  -shortest videos/{:03d}.mp4 -loglevel quiet -y".format(
            number, number, number
        )
    )


def render_video():
    cwd = os.getcwd()
    nr_images = len(os.listdir(cwd + "/images"))
    print("Generating parts")
    with open("videos_paths.txt", "w") as file:
        for n in range(nr_images):
            print(n)
            get_image_audio(n)
            file.write("file videos/{:03d}.mp4\n".format(n))
    print("Concatenating every part")
    os.system(
        "ffmpeg -f concat -i videos_paths.txt -vf 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' output.mp4 -loglevel quiet -y"
    )
    os.system("rm videos_paths.txt")


def cleanup():
    os.system("rm -rf audios")
    os.system("rm -rf images")
    os.system("rm -rf videos")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide the thread url:\nmain.py thread-url <limit>")
        sys.exit()

    cleanup()

    os.makedirs("audios")
    os.makedirs("images")
    os.makedirs("videos")

    url = sys.argv[1]
    limit = None
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])

    reddit = praw.Reddit("bot1")

    submission = reddit.submission(url=url)

    title = submission.title
    description = submission.selftext.replace("\n", " ")
    author = submission.author.name

    intro_img(author, title, description)
    read_save(title + ". " + description, 0)

    submission.comments.replace_more(limit=None)
    counter = 1
    for top_level_comment in submission.comments:
        if (limit is not None and counter > limit) or top_level_comment.author is None:
            break
        author = top_level_comment.author.name
        comment = top_level_comment.body.replace("\n", " ")
        print(counter, comment)
        post_img(author, comment, counter)
        read_save(comment, counter)
        counter += 1

    render_video()

    cleanup()

    pass

# submission.comments.replace_more(limit=0)
# submission.comments.replace_more(limit=None)
# for top_level_comment in submission.comments:
# comment = top_level_comment.body
# for second_level_comment in top_level_comment.replies:
# print(second_level_comment.body)
