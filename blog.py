""" Basic blog using webpy 0.3 """
import time
import web
import model

### Url mappings

urls = (
    '/', 'Index',
    '/view/(.+)', 'View',
    '/new', 'New',
    '/delete/(.+)', 'Delete',
    '/edit/(.+)', 'Edit',
)

def timestr(epoch):
    return time.strftime('%a, %b.%d %H:%M', time.localtime(epoch))

### Templates
t_globals = {
    'datestr': web.datestr,
    'timestr': timestr
}
render = web.template.render('templates', base='base', globals=t_globals)


class Index:

    def GET(self):
        """ Show page """
        posts = model.get_posts()
        return render.index(posts)


class View:

    def GET(self, post_id):
        """ View single post """
        post = model.get_post(post_id)
        return render.view(post)


class New:

    form = web.form.Form(
        web.form.Textbox('title', web.form.notnull, 
            size=30,
            description="Post title:"),
        web.form.Textarea('content', web.form.notnull, 
            rows=30, cols=80,
            description="Post content:"),
        web.form.Button('Post entry'),
    )

    def GET(self):
        form = self.form()
        return render.new(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        model.new_post(form.d.title, form.d.content)
        raise web.seeother('/')


class Delete:

    def POST(self, post_id):
        model.del_post(post_id)
        raise web.seeother('/')


class Edit:

    def GET(self, post_id):
        post = model.get_post(post_id)
        form = New.form()
        form.fill(post)
        return render.edit(post, form)


    def POST(self, post_id):
        form = New.form()
        post = model.get_post(post_id)
        if not form.validates():
            return render.edit(post, form)
        model.update_post(post_id, form.d.title, form.d.content)
        raise web.seeother('/')


app = web.application(urls, globals())

if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    app.run()