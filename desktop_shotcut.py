import gi
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GObject, Gtk, Pango

app_used = None
app_name = None

class AppChooserComboBox(Gtk.ComboBox):
    """GTK+ 3 ComboBox allowing selection of an installed application.
    
    The Gio.AppInfo of the currently selected app is made available via the
    get_selected_app method.
    """

    def __init__(self):
        super().__init__()

        self._mime_types = []
        self._filter_term = ""
        self._use_regex = False
        self._app_list = []

        pixbuf_renderer = Gtk.CellRendererPixbuf()
        pixbuf_renderer.set_alignment(0, 0.5)
        pixbuf_renderer.set_padding(2, 0)
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_alignment(0, 0.5)

        self._app_store = Gtk.ListStore(str, str)
        self.set_model(self._app_store)
        self.pack_start(pixbuf_renderer, True)
        self.add_attribute(pixbuf_renderer, "icon_name", 0)
        self.pack_start(text_renderer, True)
        self.add_attribute(text_renderer, "text", 1)

    def get_mime_types(self):
        """Get the list of mime types from which to select apps.
        
        :return: List of mime types to be displayed.
        """
        return self._mime_types

    def get_filter_term(self):
        """Get the string used for filtering apps by display name.
        
        :return: String used for filtering apps by display name.
        """
        return self._filter_term

    def get_selected_app(self):
        """Get the Gio.AppInfo of the app currently selected in the combo box.
        
        :return: Gio.AppInfo of currently selected app.
        """
        selection_index = self.get_active()
        if selection_index == 0:  # When "Choose An App)" is selected
            return None
        else:
            return self._app_list[selection_index - 1]

    def get_use_regex(self):
        """ Get whether the filter term should be used as a regex pattern.
        
        :return: Whether the filter term is used as a regex pattern.
        """
        return self._use_regex

    def populate(self):
        """Populate the combo box with installed applications.
        
        :return: None
        """
        app_list = Gio.AppInfo.get_all()
        self._app_list = []

        for app in app_list:
            if self._filter_term:
                if self._use_regex:
                    if not re.search(self._filter_term,
                                     app.get_display_name()):
                        continue
                else:
                    if not self._filter_term.lower() in \
                            app.get_display_name().lower():
                        continue

            if self._mime_types:
                supported_types_specific = app.get_supported_types()
                supported_types_general = []
                for mime_type in supported_types_specific:
                    mime_type = mime_type.split('/')
                    if mime_type[0] not in supported_types_general:
                        supported_types_general += [mime_type[0]]
                no_match = True
                for mime_type in self._mime_types:
                    if mime_type in supported_types_general or \
                                    mime_type in supported_types_specific:
                        no_match = False
                        break
                if no_match:
                    continue

            self._app_list += [app]

        self._app_list.sort(key=lambda app: app.get_display_name())

        self._app_store.clear()
        self._app_store.append(["gtk-search", "(Choose An App)"])
        for app in self._app_list:
            icon = app.get_icon()
            icon_name = icon.to_string() if icon else "gtk-missing-icon"
            self._app_store.append([icon_name, app.get_display_name()])
        self.set_active(0)
        self.show_all()

    def set_mime_types(self, mime_types):
        """ Get the list of mime types from which to select apps.
        
        Combobox will not update mime types once it has been shown.
        
        :param mime_types: List of mime types to allow selection from.
        :return: None
        """
        if not type(mime_types) == list:
            raise TypeError("must be type list, not " +
                            type(mime_types).__name__)
        self._mime_types = list(set(mime_types))

    def set_filter_term(self, filter_term):
        """Set the string used for filtering apps by display name.
        
        If use_regex is True, the provided string will be used as the pattern
        for a regex match, otherwise basic case-insensitive matching is used.
        
        Combobox will not update the filter term once it has been shown.
        
        :param filter_term: String used for filtering apps by display name.
        :return: None
        """
        if not type(filter_term) == str:
            raise TypeError("must be type str, not " +
                            type(filter_term).__name__)
        self._filter_term = filter_term

    def set_use_regex(self, use_regex):
        """Set whether or not regex terms are used to filter apps.
        
        If use_regex is True, the filter term will be used as the pattern for a
        regex match, otherwise basic case-insensitive matching is used.
        
        Combobox will not update this value once it has been shown.
        
        :param use_regex: Whether the filter term is used as a regex pattern.
        :return: None
        """
        if not type(use_regex) == bool:
            raise TypeError("must be type bool, not " +
                            type(use_regex).__name__)
        self._use_regex = use_regex

class MyWindow(Gtk.Window):
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title('Desktop Shotcuts')

        box = Gtk.Box()
        icon_chooser_combo = AppChooserComboBox()
        icon_chooser_combo.set_mime_types(['application'])
        icon_chooser_combo.populate()
        icon_chooser_combo.connect('changed', print_selection)
        
        box.pack_start(icon_chooser_combo, True, True, 0)

        button1 = Gtk.Button(label="Criar Atalho")
        button2 = Gtk.Button(label="Sair")
        button1.connect("clicked", self.on_button1_clicked)
        button2.connect("clicked", self.on_button2_clicked)
        box.pack_start(button1, True,True, 0)
        box.pack_start(button2, True,True, 0)
        # Start
        self.window.add(box)
        self.window.connect('destroy', Gtk.main_quit)
        self.window.show_all()
            
        Gtk.main()

    def on_button1_clicked(self, widget):
        try:
            print(app_used)
            os.system("cp " + app_used + " ~/Área\ de\ trabalho")
        except:
            try:
                os.system("cp " + app_used + " ~/Desktop")
                print("2 tentativa")
            except:
                print("Failed to create shortcut")


    def on_button2_clicked(self, widget):
        print("Exit")
        Gtk.main_quit()

def print_selection(widget):
    selection = widget.get_selected_app()
    if not selection:
        print("No app was selected.")
        print(None)
    else:
        print("{0} was selected.".format(selection.get_display_name()))
        print(selection)
    global app_used
    global app_name
    app_used =  selection.get_filename()
    app_name = selection.get_display_name()
    

if __name__ == '__main__':
    MyWindow()
