# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.checkbox import CheckBox
from kivy.uix.modalview import ModalView

from database import DatabaseManager
from report_generator import ReportGenerator
from whatsapp_service import WhatsAppService
from backup_service import BackupService
from kivy.clock import Clock

# Modification 1: Make window always fit to screen size
Window.clearcolor = (0.95, 0.95, 0.95, 1)
Window.maximize()

import os

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')


class ProfessionalButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.8, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = '40dp'
        self.background_normal = ''
        self.background_down = ''


class ProfessionalTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 1)
        self.foreground_color = (0, 0, 0, 1)
        self.size_hint_y = None
        self.height = '40dp'
        self.multiline = False
        self.padding = [10, 10]
        self.font_name = "assets/fonts/NotoSansDevanagari-Regular.ttf"
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class HeaderLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (1, 1, 1, 1)
        self.font_size = '20sp'
        self.font_name = "assets/fonts/NotoSansDevanagari-Regular.ttf"
        self.bold = True
        self.size_hint_y = None
        self.height = '50dp'
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class SectionLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.3, 0.3, 0.3, 1)
        self.font_size = '20sp'
        self.font_name = "assets/fonts/NotoSansDevanagari-Regular.ttf"
        self.bold = True
        self.size_hint_y = None
        self.height = '40dp'
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class FormLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.2, 0.2, 0.2, 1)
        self.font_size = '15sp'
        self.font_name = "assets/fonts/NotoSansDevanagari-Regular.ttf"
        self.size_hint_y = None
        self.height = '30dp'
        self.halign = 'justify'
        self.valign = 'middle'
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class UserAddScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.camera = None
        self.temp_image_path = None
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="Add New User", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        # Scrollable content
        scroll_content = ScrollView()
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Name
        form_layout.add_widget(FormLabel(text="Full Name/पूर्ण नाव (Alphabets only)"))
        self.name_input = ProfessionalTextInput(hint_text="Enter Full Name पूर्ण नाव प्रविष्ट करा ")
        self.name_input.bind(on_text_validate=self.validate_name)
        form_layout.add_widget(self.name_input)

        # Aadhar
        form_layout.add_widget(FormLabel(text="Aadhar Number/आधार नंबर (12 digits)"))
        self.aadhar_input = ProfessionalTextInput(hint_text="Enter Aadhar Number आधार नंबर प्रविष्ट करा")
        # Modification 4: Strict validation for Aadhar number
        self.aadhar_input.input_filter = 'int'
        self.aadhar_input.bind(
            on_text_validate=self.validate_aadhar,
            text=self.on_aadhar_text
        )
        form_layout.add_widget(self.aadhar_input)

        # Mobile
        form_layout.add_widget(FormLabel(text="Mobile Number/मोबाईल नंबर (10 digits) "))
        self.mobile_input = ProfessionalTextInput(hint_text="Enter Mobile Number मोबाईल नंबर प्रविष्ट करा")
        # Modification 5: Strict validation for Mobile number
        self.mobile_input.input_filter = 'int'
        self.mobile_input.bind(
            on_text_validate=self.validate_mobile,
            text=self.on_mobile_text
        )
        form_layout.add_widget(self.mobile_input)

        # Gender
        form_layout.add_widget(FormLabel(text="Gender"))
        self.gender_spinner = Spinner(
            text='Male',
            values=('Male', 'Female', 'Other'),
            size_hint_y=None,
            height='40dp',
            background_color=(1, 1, 1, 1),
            font_name="assets/fonts/NotoSansDevanagari-Regular.ttf",
            color=(0, 0, 0, 1)
        )
        form_layout.add_widget(self.gender_spinner)

        # Joining Date
        form_layout.add_widget(FormLabel(text="Joining Date"))
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.date_input = ProfessionalTextInput(text=datetime.now().strftime("%Y-%m-%d"))
        # Modification 7: Strict validation for Joining date
        self.date_input.bind(
            text=self.on_date_text
        )
        date_btn = ProfessionalButton(text="Pick Date", size_hint_x=0.3)
        date_btn.bind(on_press=self.show_date_picker)
        date_layout.add_widget(self.date_input)
        date_layout.add_widget(date_btn)
        form_layout.add_widget(date_layout)

        # Address
        form_layout.add_widget(FormLabel(text="Address"))
        self.address_input = TextInput(
            size_hint_y=None,
            height='80dp',
            multiline=True,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            font_name="assets/fonts/NotoSansDevanagari-Regular.ttf",
            hint_text = "Enter Address पत्ता प्रविष्ट करा"
        )
        form_layout.add_widget(self.address_input)

        # Seat Selection
        form_layout.add_widget(FormLabel(text="Select Seat"))
        seat_btn = ProfessionalButton(text="Open Seat Chart")
        seat_btn.bind(on_press=self.open_seat_chart)
        form_layout.add_widget(seat_btn)
        self.seat_label = FormLabel(text="Click on Open Seat Chart Button to Select Seat")
        form_layout.add_widget(self.seat_label)

        # Monthly Fees
        form_layout.add_widget(FormLabel(text="Monthly Fees"))
        self.fees_input = ProfessionalTextInput(hint_text="Enter Monthly Fees")
        # Modification 6: Strict validation for Monthly fees
        self.fees_input.input_filter = 'int'
        self.fees_input.bind(
            on_text_validate=self.validate_fees,
            text=self.on_fees_text
        )
        form_layout.add_widget(self.fees_input)

        # Image
        form_layout.add_widget(FormLabel(text="Profile Image"))
        img_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='120dp')
        self.image_path = ""
        self.image_preview = Image(
            source='assets/default_avatar.png',
            size_hint_x=0.6,
            allow_stretch=True
        )

        # Image buttons layout
        img_buttons_layout = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=5)
        upload_btn = ProfessionalButton(text="Upload Image")
        capture_btn = ProfessionalButton(text="Capture Image")

        upload_btn.bind(on_press=self.upload_image)
        capture_btn.bind(on_press=self.capture_image)

        img_buttons_layout.add_widget(upload_btn)
        img_buttons_layout.add_widget(capture_btn)

        img_layout.add_widget(self.image_preview)
        img_layout.add_widget(img_buttons_layout)
        form_layout.add_widget(img_layout)

        # Add Button
        add_btn = ProfessionalButton(text="Add User", background_color=(0.2, 0.8, 0.2, 1))
        add_btn.bind(on_press=self.add_user)
        form_layout.add_widget(add_btn)

        scroll_content.add_widget(form_layout)
        layout.add_widget(scroll_content)
        self.add_widget(layout)

    # Modification 4: Aadhar number validation - only digits and max length 12
    def on_aadhar_text(self, instance, value):
        if len(value) > 12:
            instance.text = value[:12]
        # Ensure only digits
        if value and not value.isdigit():
            instance.text = ''.join(filter(str.isdigit, value))

    # Modification 5: Mobile number validation - only digits and max length 10
    def on_mobile_text(self, instance, value):
        if len(value) > 10:
            instance.text = value[:10]
        # Ensure only digits
        if value and not value.isdigit():
            instance.text = ''.join(filter(str.isdigit, value))

    # Modification 6: Monthly fees validation - only digits and max length 4
    def on_fees_text(self, instance, value):
        if len(value) > 4:
            instance.text = value[:4]
        # Ensure only digits
        if value and not value.isdigit():
            instance.text = ''.join(filter(str.isdigit, value))

    # Modification 7: Joining date validation - only digits and "-", max length 10
    def on_date_text(self, instance, value):
        if len(value) > 10:
            instance.text = value[:10]
        # Allow only digits and hyphen
        if value:
            filtered_text = ''.join(c for c in value if c.isdigit() or c == '-')
            if filtered_text != value:
                instance.text = filtered_text

    def refresh_screen(self, instance):
        self.clear_form()
        self.show_popup("Info", "Screen refreshed successfully")

    def validate_name(self, instance):
        name = self.name_input.text
        if not all(c.isalpha() or c.isspace() for c in name) and name != "":
            self.name_input.background_color = (1, 0.8, 0.8, 1)
        else:
            self.name_input.background_color = (1, 1, 1, 1)

    def validate_aadhar(self, instance):
        aadhar = self.aadhar_input.text
        if not (aadhar.isdigit() and len(aadhar) == 12) and aadhar != "":
            self.aadhar_input.background_color = (1, 0.8, 0.8, 1)
        else:
            self.aadhar_input.background_color = (1, 1, 1, 1)

    def validate_mobile(self, instance):
        mobile = self.mobile_input.text
        if not (mobile.isdigit() and len(mobile) == 10) and mobile != "":
            self.mobile_input.background_color = (1, 0.8, 0.8, 1)
        else:
            self.mobile_input.background_color = (1, 1, 1, 1)

    def validate_fees(self, instance):
        fees = self.fees_input.text
        if not (fees.isdigit() and len(fees) <= 4) and fees != "":
            self.fees_input.background_color = (1, 0.8, 0.8, 1)
        else:
            self.fees_input.background_color = (1, 1, 1, 1)

    def show_date_picker(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        date_input = ProfessionalTextInput(text=self.date_input.text)

        def set_date(inst):
            self.date_input.text = date_input.text
            popup.dismiss()

        btn = ProfessionalButton(text='Set Date')
        btn.bind(on_press=set_date)

        content.add_widget(FormLabel(text='Enter date (YYYY-MM-DD)'))
        content.add_widget(date_input)
        content.add_widget(btn)

        popup = Popup(title='Select Date', content=content, size_hint=(0.8, 0.4))
        popup.open()

    def open_seat_chart(self, instance):
        popup = SeatChartPopup(callback=self.on_seat_select)
        popup.open()

    def on_seat_select(self, seat_number):
        self.seat_label.text = f"Selected Seat: {seat_number}"
        self.selected_seat = seat_number

    def upload_image(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        filechooser = FileChooserIconView()
        filechooser.filters = ['*.png', '*.jpg', '*.jpeg']

        def select_file(inst):
            if filechooser.selection:
                selected_file = filechooser.selection[0]
                try:
                    import shutil
                    filename = os.path.basename(selected_file)
                    destination = f"assets/user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    shutil.copy2(selected_file, destination)

                    self.image_path = destination
                    self.image_preview.source = destination
                    popup.dismiss()
                    self.show_popup("Success", "Image uploaded successfully")
                except Exception as e:
                    self.show_popup("Error", f"Failed to upload image: {str(e)}")

        def cancel_selection(inst):
            popup.dismiss()

        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        select_btn = ProfessionalButton(text='Select Image')
        cancel_btn = ProfessionalButton(text='Cancel')

        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=cancel_selection)

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(filechooser)
        content.add_widget(btn_layout)

        popup = Popup(title='Select Profile Image', content=content, size_hint=(0.9, 0.8))
        popup.open()

    def capture_image(self, instance):
        """Open camera for image capture with proper area capture"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Camera widget with proper sizing
        from kivy.uix.camera import Camera
        self.camera = Camera(resolution=(640, 480), play=True)

        # Container for camera with fixed aspect ratio
        camera_container = BoxLayout(orientation='vertical', size_hint_y=0.7)
        camera_container.add_widget(self.camera)
        content.add_widget(camera_container)

        # Instructions
        instructions = Label(
            text="Position face in the center and click Capture",
            size_hint_y=None,
            height='30dp',
            text_size=(None, None),
            halign='center'
        )
        content.add_widget(instructions)

        # Buttons layout
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)

        capture_btn = ProfessionalButton(text="Capture")
        cancel_btn = ProfessionalButton(text="Cancel")

        # Preview image (initially hidden)
        self.captured_image = Image(
            size_hint_y=None,
            height='0dp',
            allow_stretch=True,
            keep_ratio=True
        )
        content.add_widget(self.captured_image)

        # Second set of buttons (Use/Retake - initially hidden)
        self.confirm_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='0dp', spacing=10)
        use_btn = ProfessionalButton(text="Use This Photo")
        retake_btn = ProfessionalButton(text="Retake")
        self.confirm_btn_layout.add_widget(use_btn)
        self.confirm_btn_layout.add_widget(retake_btn)
        content.add_widget(self.confirm_btn_layout)

        # Store the captured image path
        self.temp_image_path = None

        def take_picture(inst):
            """Capture picture from camera with proper area"""
            try:
                # Create timestamp for unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_path = f"assets/temp_captured_{timestamp}.jpg"
                final_temp_path = f"assets/captured_{timestamp}.jpg"

                # Ensure assets directory exists
                if not os.path.exists('assets'):
                    os.makedirs('assets')

                # Capture the image from camera only (not the whole screen)
                self.camera.export_to_png(temp_path)

                # Process the image to ensure proper size and add background if needed
                from PIL import Image as PILImage, ImageDraw

                # Open the captured image
                pil_image = PILImage.open(temp_path)

                # Create a new image with black background (portrait orientation)
                target_width = 400
                target_height = 500
                new_image = PILImage.new('RGB', (target_width, target_height), 'white')

                # Calculate position to center the camera image
                img_width, img_height = pil_image.size

                # Resize maintaining aspect ratio
                if img_width / img_height > target_width / target_height:
                    # Image is wider than target
                    new_height = target_height
                    new_width = int(img_width * target_height / img_height)
                else:
                    # Image is taller than target
                    new_width = target_width
                    new_height = int(img_height * target_width / img_width)

                resized_img = pil_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)

                # Calculate position to center
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2

                # Paste the resized image onto the black background
                new_image.paste(resized_img, (x_offset, y_offset))

                # Save the final image
                new_image.save(final_temp_path, 'JPEG', quality=95)

                # Clean up temporary file
                try:
                    os.remove(temp_path)
                except:
                    pass

                # Store the path
                self.temp_image_path = final_temp_path

                # Show preview
                self.captured_image.source = final_temp_path
                self.captured_image.height = '200dp'

                # Hide camera and show confirmation buttons
                camera_container.height = '0dp'
                instructions.height = '0dp'
                capture_btn.disabled = True
                cancel_btn.disabled = True

                # Show confirmation buttons
                self.confirm_btn_layout.height = '50dp'

                # STOP CAMERA IMMEDIATELY AFTER CAPTURE
                if self.camera:
                    self.camera.play = False

            except Exception as e:
                self.show_popup("Error", f"Failed to capture image: {str(e)}")
                # Clean up on error
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass

        def retake_picture(inst):
            """Retake picture"""
            # Show camera again
            camera_container.height = '300dp'
            instructions.height = '30dp'
            self.captured_image.height = '0dp'
            capture_btn.disabled = False
            cancel_btn.disabled = False

            # Hide confirmation buttons
            self.confirm_btn_layout.height = '0dp'

            # Clear temporary image
            if self.temp_image_path and os.path.exists(self.temp_image_path):
                try:
                    os.remove(self.temp_image_path)
                except:
                    pass
            self.temp_image_path = None

            # RESTART CAMERA FOR RETAKE
            if self.camera:
                self.camera.play = True

        def use_picture(inst):
            """Use the captured picture"""
            try:
                if self.temp_image_path and os.path.exists(self.temp_image_path):
                    # Create final filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    final_image_path = f"assets/user_profile_{timestamp}.jpg"

                    # Copy to final location
                    import shutil
                    shutil.copy2(self.temp_image_path, final_image_path)

                    # Set the image in the form
                    self.image_path = final_image_path
                    self.image_preview.source = final_image_path

                    # Clean up temporary file
                    try:
                        if os.path.exists(self.temp_image_path):
                            os.remove(self.temp_image_path)
                    except:
                        pass

                    # RELEASE CAMERA RESOURCES
                    if self.camera:
                        self.camera.play = False
                        self.camera = None

                    popup.dismiss()

                    self.show_popup("Success", "Profile image saved successfully!")
                else:
                    self.show_popup("Error", "No image captured. Please try again.")

            except Exception as e:
                self.show_popup("Error", f"Failed to save image: {str(e)}")

        def cancel_capture(inst):
            """Cancel camera operation and release resources"""
            # Clean up temporary file
            try:
                if hasattr(self, 'temp_image_path') and self.temp_image_path and os.path.exists(self.temp_image_path):
                    os.remove(self.temp_image_path)
            except:
                pass

            # RELEASE CAMERA RESOURCES PROPERLY
            if self.camera:
                self.camera.play = False
                self.camera = None

            popup.dismiss()

        # Bind buttons
        capture_btn.bind(on_press=take_picture)
        cancel_btn.bind(on_press=cancel_capture)
        retake_btn.bind(on_press=retake_picture)
        use_btn.bind(on_press=use_picture)

        # Add initial buttons
        btn_layout.add_widget(capture_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Capture Profile Image",
            content=content,
            size_hint=(0.9, 0.9),
            auto_dismiss=False
        )

        def on_dismiss(instance):
            """Stop camera and clean up when popup is dismissed"""
            # Clean up temporary file if popup is dismissed without using the photo
            try:
                if hasattr(self, 'temp_image_path') and self.temp_image_path and os.path.exists(self.temp_image_path):
                    os.remove(self.temp_image_path)
            except:
                pass

            # RELEASE CAMERA RESOURCES WHEN POPUP IS DISMISSED
            if self.camera:
                self.camera.play = False
                self.camera = None

        popup.bind(on_dismiss=on_dismiss)
        popup.open()

    def validate_inputs(self):
        if not all(c.isalpha() or c.isspace() for c in self.name_input.text.strip()):
            return False, "Name should contain only alphabets and spaces"

        if not (self.aadhar_input.text.isdigit() and len(self.aadhar_input.text) == 12):
            return False, "Aadhar should be exactly 12 digits"

        if not (self.mobile_input.text.isdigit() and len(self.mobile_input.text) == 10):
            return False, "Mobile should be exactly 10 digits"

        if not (self.fees_input.text.isdigit() and len(self.fees_input.text) <= 4):
            return False, "Fees should be numeric and up to 4 digits"

        if not hasattr(self, 'selected_seat'):
            return False, "Please select a seat"

        return True, "Valid"

    def add_user(self, instance):
        valid, message = self.validate_inputs()
        if not valid:
            self.show_popup("Error", message)
            return

        user_data = {
            'name': self.name_input.text.strip(),
            'aadhar': self.aadhar_input.text,
            'mobile': self.mobile_input.text,
            'gender': self.gender_spinner.text,
            'joining_date': self.date_input.text,
            'address': self.address_input.text.strip(),
            'seat_number': getattr(self, 'selected_seat', ''),
            'monthly_fees': int(self.fees_input.text),
            'image_path': self.image_path,
            'status': 'Active'
        }

        success, message = self.db.add_user(user_data)
        if success:
            self.show_popup("Success", f"User added successfully! User ID: {message}")
            self.clear_form()
        else:
            self.show_popup("Error", message)

    def clear_form(self):
        self.name_input.text = ""
        self.aadhar_input.text = ""
        self.mobile_input.text = ""
        self.gender_spinner.text = "Male"
        self.date_input.text = datetime.now().strftime("%Y-%m-%d")
        self.address_input.text = ""
        self.seat_label.text = "No seat selected"
        self.fees_input.text = ""
        self.image_path = ""
        self.image_preview.source = "assets/default_avatar.png"
        if hasattr(self, 'selected_seat'):
            delattr(self, 'selected_seat')

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class ViewUsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="View Users", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        # Search section
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.search_input = ProfessionalTextInput(hint_text="Search by ID/Name/Aadhar")
        search_btn = ProfessionalButton(text="Search", size_hint_x=0.3)
        search_btn.bind(on_press=self.search_user)
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        layout.add_widget(search_layout)

        # Users list
        scroll = ScrollView()
        self.users_tree = TreeView(hide_root=True, size_hint=(1, 1))
        scroll.add_widget(self.users_tree)
        layout.add_widget(scroll)

        # Action buttons
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        edit_btn = ProfessionalButton(text="Edit User")
        delete_btn = ProfessionalButton(text="Delete User")
        toggle_btn = ProfessionalButton(text="Activate/Deactivate")

        edit_btn.bind(on_press=self.edit_user)
        delete_btn.bind(on_press=self.delete_user)
        toggle_btn.bind(on_press=self.toggle_status)

        action_layout.add_widget(edit_btn)
        action_layout.add_widget(delete_btn)
        action_layout.add_widget(toggle_btn)
        layout.add_widget(action_layout)

        self.add_widget(layout)
        self.load_users()

    def refresh_screen(self, instance):
        self.load_users()
        self.search_input.text = ""
        self.show_popup("Info", "Screen refreshed successfully")

    def load_users(self):
        self.users_tree.clear_widgets()
        users = self.db.get_all_users()
        # Use a dictionary to track unique users by ID
        unique_users = {}

        for user in users:
            user_id = user['user_id']
            if user_id not in unique_users:
                unique_users[user_id] = user

                status_color = (1, 0, 0, 1) if user['status'] == 'Inactive' else (0.2, 0.2, 0.2, 1)
                if self.db.is_user_defaulter(user['user_id']):
                    status_color = (1, 0, 0, 1)

                text = f"ID: {user['user_id']} | {user['name']} | {user['mobile_number']} | Fees: ₹{user['monthly_fees']} | Status: {user['status']}"
                node = TreeViewLabel(text=text, color=status_color)
                node.user_data = user
                self.users_tree.add_node(node)

    def search_user(self, instance):
        # Modification 3: Clear screen before showing new search results
        self.users_tree.clear_widgets()
        search_term = self.search_input.text
        users = self.db.search_users(search_term)

        # Use a dictionary to track unique users by ID
        unique_users = {}

        for user in users:
            user_id = user['user_id']
            if user_id not in unique_users:
                unique_users[user_id] = user
                text = f"ID: {user['user_id']} | {user['name']} | Mobile: {user['mobile_number']}"
                node = TreeViewLabel(text=text)
                node.user_data = user
                self.users_tree.add_node(node)

    def edit_user(self, instance):
        selected = self.get_selected_user()
        if selected:
            self.show_edit_popup(selected)

    def delete_user(self, instance):
        selected = self.get_selected_user()
        if selected:
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text=f"Delete user {selected['name']} (ID: {selected['user_id']})?"))

            btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
            yes_btn = ProfessionalButton(text="Yes", background_color=(0.8, 0.2, 0.2, 1))
            no_btn = ProfessionalButton(text="No")

            def confirm_delete(inst):
                if self.db.delete_user(selected['user_id']):
                    self.show_popup("Success", "User deleted successfully")
                    self.load_users()
                else:
                    self.show_popup("Error", "Failed to delete user")
                popup.dismiss()

            yes_btn.bind(on_press=confirm_delete)
            no_btn.bind(on_press=lambda x: popup.dismiss())

            btn_layout.add_widget(yes_btn)
            btn_layout.add_widget(no_btn)
            content.add_widget(btn_layout)

            popup = Popup(title="Confirm Delete", content=content, size_hint=(0.8, 0.4))
            popup.open()

    def toggle_status(self, instance):
        selected = self.get_selected_user()
        if selected:
            new_status = 'Inactive' if selected['status'] == 'Active' else 'Active'
            if self.db.update_user_status(selected['user_id'], new_status):
                self.show_popup("Success", f"User status updated to {new_status}")
                self.load_users()
            else:
                self.show_popup("Error", "Failed to update status")

    def get_selected_user(self):
        for node in self.users_tree.iterate_all_nodes():
            if node.is_selected:
                return node.user_data
        self.show_popup("Error", "Please select a user first")
        return None

    def show_edit_popup(self, user_data):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        scroll = ScrollView()
        edit_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        edit_layout.bind(minimum_height=edit_layout.setter('height'))

        edit_layout.add_widget(FormLabel(text=f"Editing User: {user_data['name']} (ID: {user_data['user_id']})"))

        # Name
        edit_layout.add_widget(FormLabel(text="Name:"))
        name_input = ProfessionalTextInput(text=user_data['name'])
        edit_layout.add_widget(name_input)

        # Mobile
        edit_layout.add_widget(FormLabel(text="Mobile:"))
        mobile_input = ProfessionalTextInput(text=user_data['mobile_number'])
        edit_layout.add_widget(mobile_input)

        # Fees
        edit_layout.add_widget(FormLabel(text="Monthly Fees:"))
        fees_input = ProfessionalTextInput(text=str(user_data['monthly_fees']))
        edit_layout.add_widget(fees_input)

        # Address
        edit_layout.add_widget(FormLabel(text="Address:"))
        address_input = TextInput(
            text=user_data['address'],
            size_hint_y=None,
            height='80dp',
            multiline=True,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        edit_layout.add_widget(address_input)

        # Status
        edit_layout.add_widget(FormLabel(text="Status:"))
        status_spinner = Spinner(
            text=user_data['status'],
            values=('Active', 'Inactive'),
            size_hint_y=None,
            height='40dp',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        edit_layout.add_widget(status_spinner)

        scroll.add_widget(edit_layout)
        content.add_widget(scroll)

        def save_changes(inst):
            updated_data = {
                'user_id': user_data['user_id'],
                'name': name_input.text.strip(),
                'mobile_number': mobile_input.text,
                'monthly_fees': int(fees_input.text) if fees_input.text.isdigit() else user_data['monthly_fees'],
                'address': address_input.text,
                'status': status_spinner.text
            }

            if self.db.update_user(updated_data):
                self.show_popup("Success", "User updated successfully")
                self.load_users()
                popup.dismiss()
            else:
                self.show_popup("Error", "Failed to update user")

        save_btn = ProfessionalButton(text="Save Changes")
        save_btn.bind(on_press=save_changes)
        content.add_widget(save_btn)

        popup = Popup(title="Edit User", content=content, size_hint=(0.9, 0.8))
        popup.open()

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class PaymentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.whatsapp_service = WhatsAppService()
        self.selected_user = None
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="Payment Management", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        # Main content
        main_layout = BoxLayout(orientation='vertical', spacing=10)

        # Payment Form Section
        form_section = BoxLayout(orientation='vertical', size_hint_y=0.4)
        form_section.add_widget(SectionLabel(text="Make Payment"))

        # User Search
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.user_search_input = ProfessionalTextInput(hint_text="Search by ID/Name/Aadhar")
        search_btn = ProfessionalButton(text="Search User", size_hint_x=0.3)
        search_btn.bind(on_press=self.search_user_for_payment)
        search_layout.add_widget(self.user_search_input)
        search_layout.add_widget(search_btn)
        form_section.add_widget(search_layout)

        # Selected User Info
        self.user_info_label = FormLabel(
            text="No user selected",
            height='60dp'
        )
        form_section.add_widget(self.user_info_label)

        # Payment Details - Using GridLayout for proper alignment
        payment_details_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height='200dp')

        payment_details_layout.add_widget(FormLabel(text="Amount to Pay:"))
        self.amount_input = ProfessionalTextInput(hint_text="Enter Amount to Pay")
        self.amount_input.bind(text=self.calculate_balance)
        payment_details_layout.add_widget(self.amount_input)

        payment_details_layout.add_widget(FormLabel(text="Balance:"))
        self.balance_label = FormLabel(text="0")
        payment_details_layout.add_widget(self.balance_label)

        payment_details_layout.add_widget(FormLabel(text="Month:"))
        self.month_spinner = Spinner(
            text=datetime.now().strftime('%b'),
            values=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
            size_hint_y=None,
            height='40dp',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        payment_details_layout.add_widget(self.month_spinner)

        payment_details_layout.add_widget(FormLabel(text="Year:"))
        current_year = datetime.now().year
        self.year_spinner = Spinner(
            text=str(current_year),
            values=[str(current_year - 1), str(current_year), str(current_year + 1)],
            size_hint_y=None,
            height='40dp',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1)
        )
        payment_details_layout.add_widget(self.year_spinner)

        payment_details_layout.add_widget(FormLabel(text="Payment Date:"))
        date_layout = BoxLayout(orientation='horizontal')
        self.payment_date_input = ProfessionalTextInput(
            text=datetime.now().strftime("%Y-%m-%d"),
            size_hint_x=0.7
        )
        date_btn = ProfessionalButton(text="Pick", size_hint_x=0.3)
        date_btn.bind(on_press=self.show_payment_date_picker)
        date_layout.add_widget(self.payment_date_input)
        date_layout.add_widget(date_btn)
        payment_details_layout.add_widget(date_layout)

        form_section.add_widget(payment_details_layout)

        # Payment Actions
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        add_payment_btn = ProfessionalButton(text="Add Payment")
        edit_payment_btn = ProfessionalButton(text="Edit Payment")
        delete_payment_btn = ProfessionalButton(text="Delete Payment")

        add_payment_btn.bind(on_press=self.add_payment)
        edit_payment_btn.bind(on_press=self.edit_payment)
        delete_payment_btn.bind(on_press=self.delete_payment)

        action_layout.add_widget(add_payment_btn)
        action_layout.add_widget(edit_payment_btn)
        action_layout.add_widget(delete_payment_btn)
        form_section.add_widget(action_layout)

        main_layout.add_widget(form_section)

        # Payments List Section
        list_section = BoxLayout(orientation='vertical', size_hint_y=0.4)
        list_section.add_widget(SectionLabel(text="Payment History"))

        # Search Payments
        payment_search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.payment_search_input = ProfessionalTextInput(hint_text="Search payments...")
        payment_search_btn = ProfessionalButton(text="Search", size_hint_x=0.3)
        payment_search_btn.bind(on_press=self.search_payments)
        payment_search_layout.add_widget(self.payment_search_input)
        payment_search_layout.add_widget(payment_search_btn)
        list_section.add_widget(payment_search_layout)

        # Payments TreeView
        scroll = ScrollView()
        self.payments_tree = TreeView(hide_root=True, size_hint=(1, 1))
        scroll.add_widget(self.payments_tree)
        list_section.add_widget(scroll)

        main_layout.add_widget(list_section)
        layout.add_widget(main_layout)
        self.add_widget(layout)

        self.load_all_payments()

    def refresh_screen(self, instance):
        self.clear_payment_form()
        self.load_all_payments()
        self.show_popup("Info", "Screen refreshed successfully")

    def search_user_for_payment(self, instance):
        search_term = self.user_search_input.text
        if not search_term:
            self.show_popup("Error", "Please enter search term")
            return

        users = self.db.search_users(search_term)
        if not users:
            self.show_popup("Error", "No user found")
            return

        if len(users) == 1:
            self.select_user_for_payment(users[0])
        else:
            self.show_user_selection_popup(users)

    def show_user_selection_popup(self, users):
        content = BoxLayout(orientation='vertical', spacing=10)
        scroll = ScrollView()

        user_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        user_list.bind(minimum_height=user_list.setter('height'))

        for user in users:
            btn = ProfessionalButton(
                text=f"ID: {user['user_id']} - {user['name']} - {user['mobile_number']}",
                size_hint_y=None,
                height='40dp'
            )
            btn.user_data = user
            btn.bind(on_press=lambda x: self.select_user_for_payment(x.user_data))
            user_list.add_widget(btn)

        scroll.add_widget(user_list)
        content.add_widget(scroll)

        popup = Popup(title="Select User", content=content, size_hint=(0.9, 0.8))
        popup.open()

    def select_user_for_payment(self, user):
        self.selected_user = user
        user_info = f"Selected: {user['name']} (ID: {user['user_id']}) | Monthly Fees: ₹{user['monthly_fees']}"
        # user_info += f"Mobile: {user['mobile_number']} | Fees: ₹{user['monthly_fees']}"

        # Check for existing payment for selected month/year
        existing_payment = self.db.get_payment_by_user_month_year(
            user['user_id'],
            self.month_spinner.text,
            int(self.year_spinner.text)
        )

        payment_data = {
            'user_id': self.selected_user['user_id'],
            'month': self.month_spinner.text,
            'year': int(self.year_spinner.text)
        }
        if existing_payment:
            user_info += (f"\nExisting payment: ₹{existing_payment['amount_paid']} | "
                          f"Balance: ₹{existing_payment['balance_amount']}"
                          f" for {payment_data['month']}-{payment_data['year']}")
            self.amount_input.text = str(existing_payment['balance_amount'])
        else:
            self.amount_input.text = str(user['monthly_fees'])

        self.user_info_label.text = user_info
        self.calculate_balance(None, self.amount_input.text)

    def calculate_balance(self, instance, value):
        if not self.selected_user or not value:
            self.balance_label.text = "0"
            return

        try:
            monthly_fees = self.selected_user['monthly_fees']
            amount_paid = int(value) if value.isdigit() else 0
            balance = monthly_fees - amount_paid
            # outstanding_amount = balance - amount_paid
            # Check for existing payment
            existing_payment = self.db.get_payment_by_user_month_year(
                self.selected_user['user_id'],
                self.month_spinner.text,
                int(self.year_spinner.text)
            )

            payment_data = {
                'user_id': self.selected_user['user_id'],
                'amount_paid': amount_paid,
                'month': self.month_spinner.text,
                'year': int(self.year_spinner.text),
                'payment_date': self.payment_date_input.text,
                'balance_amount': monthly_fees - amount_paid
            }

            if existing_payment:
                # Update existing payment
                if existing_payment['balance_amount'] == 0:
                    # self.show_popup("Error", "Payment already completed for this month/year")
                    return

                new_amount_paid = existing_payment['amount_paid'] + amount_paid
                new_balance = monthly_fees - new_amount_paid

                if new_amount_paid > monthly_fees:
                    self.show_popup("Error", "Total payment cannot exceed monthly fees")
                    return

                payment_data = {
                    'payment_id': existing_payment['payment_id'],
                    'amount_paid': new_amount_paid,
                    'balance_amount': new_balance
                }
                balance = new_balance
                # success = self.db.update_payment(payment_data)
                # receipt_number = existing_payment['receipt_number']
            else:
                pass
                # Create new payment
                # success, receipt_number = self.db.add_payment(payment_data)

            self.balance_label.text = str(max(0,balance))

            if balance > 0:
                self.balance_label.color = (1, 0, 0, 1)
            else:
                self.balance_label.color = (0, 0.5, 0, 1)

        except ValueError:
            self.balance_label.text = "0"

    def show_payment_date_picker(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        date_input = ProfessionalTextInput(text=self.payment_date_input.text)

        def set_date(inst):
            self.payment_date_input.text = date_input.text
            popup.dismiss()

        btn = ProfessionalButton(text='Set Date')
        btn.bind(on_press=set_date)

        content.add_widget(FormLabel(text='Enter date (YYYY-MM-DD)'))
        content.add_widget(date_input)
        content.add_widget(btn)

        popup = Popup(title='Select Payment Date', content=content, size_hint=(0.8, 0.4))
        popup.open()

    def add_payment(self, instance):
        if not self.selected_user:
            self.show_popup("Error", "Please select a user first")
            return

        if not self.amount_input.text.isdigit():
            self.show_popup("Error", "Please enter a valid amount")
            return

        amount_paid = int(self.amount_input.text)
        monthly_fees = self.selected_user['monthly_fees']

        if amount_paid <= 0:
            self.show_popup("Error", "Amount must be greater than 0")
            return

        if amount_paid > monthly_fees:
            self.show_popup("Error", "Amount cannot exceed monthly fees")
            return

        # Check for existing payment
        existing_payment = self.db.get_payment_by_user_month_year(
            self.selected_user['user_id'],
            self.month_spinner.text,
            int(self.year_spinner.text)
        )

        payment_data = {
            'user_id': self.selected_user['user_id'],
            'amount_paid': amount_paid,
            'month': self.month_spinner.text,
            'year': int(self.year_spinner.text),
            'payment_date': self.payment_date_input.text,
            'balance_amount': monthly_fees - amount_paid
        }

        if existing_payment:
            # Update existing payment
            if existing_payment['balance_amount'] == 0:
                self.show_popup("Error", "Payment already completed for this month/year")
                return

            new_amount_paid = existing_payment['amount_paid'] + amount_paid
            new_balance = monthly_fees - new_amount_paid

            if new_amount_paid > monthly_fees:
                self.show_popup("Error", "Total payment cannot exceed monthly fees")
                return

            payment_data = {
                'payment_id': existing_payment['payment_id'],
                'amount_paid': new_amount_paid,
                'balance_amount': new_balance
            }

            success = self.db.update_payment(payment_data)
            receipt_number = existing_payment['receipt_number']
        else:
            # Create new payment
            success, receipt_number = self.db.add_payment(payment_data)

        if success:
            # Send WhatsApp notification - FIXED: Use correct payment_data structure
            message_data = {
                'amount_paid': amount_paid,
                'month': self.month_spinner.text,
                'year': int(self.year_spinner.text),
                'balance_amount': monthly_fees - amount_paid,
                'receipt_number': receipt_number,
                'payment_date': self.payment_date_input.text
            }
            self.whatsapp_service.send_payment_notification(self.selected_user, message_data)

            self.show_popup("Success", f"Payment processed successfully!\nReceipt: {receipt_number}")
            self.clear_payment_form()
            self.load_all_payments()
        else:
            self.show_popup("Error", f"Failed to process payment: {receipt_number}")

    def edit_payment(self, instance):
        selected_payment = self.get_selected_payment()
        if not selected_payment:
            self.show_popup("Error", "Please select a payment to edit")
            return

        self.show_edit_payment_popup(selected_payment)

    def delete_payment(self, instance):
        selected_payment = self.get_selected_payment()
        if not selected_payment:
            self.show_popup("Error", "Please select a payment to delete")
            return

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Delete payment {selected_payment['receipt_number']}?"))

        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        yes_btn = ProfessionalButton(text="Yes", background_color=(0.8, 0.2, 0.2, 1))
        no_btn = ProfessionalButton(text="No")

        def confirm_delete(inst):
            if self.db.delete_payment(selected_payment['payment_id']):
                self.show_popup("Success", "Payment deleted successfully")
                self.load_all_payments()
            else:
                self.show_popup("Error", "Failed to delete payment")
            popup.dismiss()

        yes_btn.bind(on_press=confirm_delete)
        no_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def get_selected_payment(self):
        for node in self.payments_tree.iterate_all_nodes():
            if node.is_selected:
                return getattr(node, 'payment_data', None)
        return None

    def show_edit_payment_popup(self, payment_data):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        amount_input = ProfessionalTextInput(text=str(payment_data['amount_paid']))

        content.add_widget(FormLabel(text=f"Edit Payment {payment_data['receipt_number']}"))
        content.add_widget(FormLabel(text="Amount:"))
        content.add_widget(amount_input)

        def save_changes(inst):
            new_amount = int(amount_input.text) if amount_input.text.isdigit() else payment_data['amount_paid']
            user = self.db.get_user_by_id(payment_data['user_id'])

            if user:
                new_balance = user['monthly_fees'] - new_amount
                update_data = {
                    'payment_id': payment_data['payment_id'],
                    'amount_paid': new_amount,
                    'balance_amount': new_balance
                }

                if self.db.update_payment(update_data):
                    self.show_popup("Success", "Payment updated successfully")
                    self.load_all_payments()
                    popup.dismiss()
                else:
                    self.show_popup("Error", "Failed to update payment")

        save_btn = ProfessionalButton(text="Save Changes")
        save_btn.bind(on_press=save_changes)
        content.add_widget(save_btn)

        popup = Popup(title="Edit Payment", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def load_all_payments(self):
        self.payments_tree.clear_widgets()
        all_users = self.db.get_all_users()
        # Use a dictionary to track unique payments by receipt number
        unique_payments = {}

        for user in all_users:
            payments = self.db.get_payments_by_user(user['user_id'])
            for payment in payments:
                receipt_no = payment['receipt_number']
                if receipt_no not in unique_payments:
                    unique_payments[receipt_no] = (payment, user)
                    text = f"{payment['payment_date']} | {user['name']} | {payment['month']} {payment['year']} | "
                    text += f"Paid: ₹{payment['amount_paid']} | Balance: ₹{payment['balance_amount']} | "
                    text += f"Receipt: {payment['receipt_number']}"

                    node = TreeViewLabel(text=text)
                    node.payment_data = payment
                    self.payments_tree.add_node(node)

    def search_payments(self, instance):
        # Modification 3: Clear screen before showing new search results
        self.payments_tree.clear_widgets()
        search_term = self.payment_search_input.text
        if not search_term:
            self.load_all_payments()
            return

        all_users = self.db.get_all_users()
        found_payments = False
        # Use a dictionary to track unique payments by receipt number
        unique_payments = {}

        for user in all_users:
            if (search_term.lower() in user['name'].lower() or
                    search_term in str(user['user_id']) or
                    search_term in user['aadhar_number']):

                payments = self.db.get_payments_by_user(user['user_id'])
                for payment in payments:
                    receipt_no = payment['receipt_number']
                    if receipt_no not in unique_payments:
                        unique_payments[receipt_no] = (payment, user)
                        text = f"{payment['payment_date']} | {user['name']} | {payment['month']} {payment['year']} | "
                        text += f"Paid: ₹{payment['amount_paid']} | Balance: ₹{payment['balance_amount']} | "
                        text += f"Receipt: {payment['receipt_number']}"

                        node = TreeViewLabel(text=text)
                        node.payment_data = payment
                        self.payments_tree.add_node(node)
                        found_payments = True

        if not found_payments:
            node = TreeViewLabel(text="No matching payments found")
            self.payments_tree.add_node(node)

    def clear_payment_form(self):
        self.selected_user = None
        self.user_search_input.text = ""
        self.user_info_label.text = "No user selected"
        self.amount_input.text = ""
        self.balance_label.text = "0"
        self.balance_label.color = (0, 0, 0, 1)
        self.payment_date_input.text = datetime.now().strftime("%Y-%m-%d")
        self.month_spinner.text = datetime.now().strftime('%b')
        current_year = datetime.now().year
        self.year_spinner.text = str(current_year)

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class DefaulterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.whatsapp_service = WhatsAppService()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="Defaulter Dashboard", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        # Search section
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.search_input = ProfessionalTextInput(hint_text="Search by Name/ID/Aadhar")
        search_btn = ProfessionalButton(text="Search", size_hint_x=0.2)
        manual_msg_btn = ProfessionalButton(text="Send Messages", size_hint_x=0.3)

        search_btn.bind(on_press=self.search_defaulters)
        manual_msg_btn.bind(on_press=self.send_manual_messages)

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        search_layout.add_widget(manual_msg_btn)
        layout.add_widget(search_layout)

        # Defaulters list
        scroll = ScrollView()
        self.defaulters_tree = TreeView(hide_root=True, size_hint=(1, 1))
        scroll.add_widget(self.defaulters_tree)
        layout.add_widget(scroll)

        # Auto message info
        info_label = Label(
            text="Double-click on a defaulter to make payment\nAutomatic messages are sent on 1st, 2nd, 3rd, and 15th of each month",
            size_hint_y=None,
            height='40dp',
            font_size='12sp',
            font_name="assets/fonts/NotoSansDevanagari-Regular.ttf",
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(info_label)

        self.add_widget(layout)
        self.load_defaulters()

        # Schedule automatic messages
        self.schedule_automatic_messages()

        # Bind double-click event
        Clock.schedule_once(self.bind_double_click, 0.5)

    def bind_double_click(self, dt):
        """Bind double-click event to treeview"""
        self.defaulters_tree.bind(on_touch_down=self.on_treeview_touch)

    def on_treeview_touch(self, instance, touch):
        """Handle double-click on treeview items"""
        if instance.collide_point(*touch.pos) and touch.is_double_tap:
            node = instance.get_node_at_pos(touch.pos)
            if node and hasattr(node, 'defaulter_data') and hasattr(node, 'user_data'):
                self.show_payment_popup(node.defaulter_data, node.user_data)
            return True
        return False

    def refresh_screen(self, instance):
        self.load_defaulters()
        self.search_input.text = ""
        self.show_popup("Info", "Screen refreshed successfully")

    def load_defaulters(self):
        self.defaulters_tree.clear_widgets()
        defaulters = self.db.get_defaulters()

        if not defaulters:
            node = TreeViewLabel(text="No defaulters found")
            self.defaulters_tree.add_node(node)
            return

        # Use a dictionary to track unique defaulters by user_id + month + year
        unique_defaulters = {}

        for defaulter in defaulters:
            user = self.db.get_user_by_id(defaulter['user_id'])
            if user and user['status'] == 'Active':
                defaulter_key = f"{user['user_id']}-{defaulter['month']}-{defaulter['year']}"
                if defaulter_key not in unique_defaulters:
                    unique_defaulters[defaulter_key] = (defaulter, user)
                    text = f"{user['name']} | {defaulter['month']} {defaulter['year']} | "
                    text += f"Balance: ₹{defaulter['balance_amount']} | Mobile: {user['mobile_number']}"

                    node = TreeViewLabel(
                        text=text,
                        color=(0.8, 0.2, 0.2, 1)  # Red color for defaulters
                    )
                    node.defaulter_data = defaulter
                    node.user_data = user
                    self.defaulters_tree.add_node(node)

    def search_defaulters(self, instance):
        # Modification 3: Clear screen before showing new search results
        self.defaulters_tree.clear_widgets()
        search_term = self.search_input.text
        if not search_term:
            self.load_defaulters()
            return

        defaulters = self.db.get_defaulters()
        # Use a dictionary to track unique defaulters by user_id + month + year
        unique_defaulters = {}

        for defaulter in defaulters:
            user = self.db.get_user_by_id(defaulter['user_id'])
            if user and user['status'] == 'Active':
                if (search_term.lower() in user['name'].lower() or
                        search_term in str(user['user_id']) or
                        search_term in user['aadhar_number']):
                    defaulter_key = f"{user['user_id']}-{defaulter['month']}-{defaulter['year']}"
                    if defaulter_key not in unique_defaulters:
                        unique_defaulters[defaulter_key] = (defaulter, user)
                        text = f"{user['name']} | {defaulter['month']} {defaulter['year']} | "
                        text += f"Balance: ₹{defaulter['balance_amount']}"

                        node = TreeViewLabel(text=text, color=(0.8, 0.2, 0.2, 1))
                        node.defaulter_data = defaulter
                        node.user_data = user
                        self.defaulters_tree.add_node(node)

        if not unique_defaulters:
            node = TreeViewLabel(text="No matching defaulters found")
            self.defaulters_tree.add_node(node)

    def show_payment_popup(self, defaulter_data, user_data):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        content.add_widget(Label(
            text=f"Pay Balance for {user_data['name']}",
            font_size='20sp',
            font_name="assets/fonts/NotoSansDevanagari-Regular.ttf",
            bold=True
        ))

        content.add_widget(Label(
            text=f"Month: {defaulter_data['month']} {defaulter_data['year']}"
        ))

        content.add_widget(Label(
            text=f"Outstanding Balance: ₹{defaulter_data['balance_amount']}"
        ))

        amount_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        amount_layout.add_widget(Label(text="Amount to Pay:"))
        self.payment_amount_input = ProfessionalTextInput(text=str(defaulter_data['balance_amount']))
        amount_layout.add_widget(self.payment_amount_input)
        content.add_widget(amount_layout)

        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        full_payment_btn = ProfessionalButton(text="Pay Full", background_color=(0.2, 0.8, 0.2, 1))
        partial_payment_btn = ProfessionalButton(text="Pay Partial")
        cancel_btn = ProfessionalButton(text="Cancel")

        full_payment_btn.bind(on_press=lambda x: self.process_payment(
            defaulter_data, user_data, defaulter_data['balance_amount'], popup))
        partial_payment_btn.bind(on_press=lambda x: self.process_payment(
            defaulter_data, user_data,
            int(self.payment_amount_input.text) if self.payment_amount_input.text.isdigit() else 0, popup))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(full_payment_btn)
        btn_layout.add_widget(partial_payment_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Make Payment", content=content, size_hint=(0.9, 0.5))
        self.current_payment_popup = popup
        popup.open()

    def process_payment(self, defaulter_data, user_data, amount, popup):
        if amount <= 0:
            self.show_popup("Error", "Please enter a valid amount")
            return

        if amount > defaulter_data['balance_amount']:
            self.show_popup("Error", "Amount cannot exceed outstanding balance")
            return

        # Check for existing payment for this month and year
        existing_payment = self.db.get_payment_by_user_month_year(
            user_data['user_id'],
            defaulter_data['month'],
            defaulter_data['year']
        )

        if existing_payment:
            # Update existing payment
            new_amount_paid = existing_payment['amount_paid'] + amount
            new_balance = user_data['monthly_fees'] - new_amount_paid

            if new_amount_paid > user_data['monthly_fees']:
                self.show_popup("Error", "Total payment cannot exceed monthly fees")
                return

            payment_data = {
                'payment_id': existing_payment['payment_id'],
                'amount_paid': new_amount_paid,
                'balance_amount': new_balance
            }

            success = self.db.update_payment(payment_data)
            receipt_number = existing_payment['receipt_number']
        else:
            # Create new payment
            payment_data = {
                'user_id': user_data['user_id'],
                'amount_paid': amount,
                'month': defaulter_data['month'],
                'year': defaulter_data['year'],
                'payment_date': datetime.now().strftime("%Y-%m-%d"),
                'balance_amount': user_data['monthly_fees'] - amount
            }

            success, receipt_number = self.db.add_payment(payment_data)

        if success:
            # Send WhatsApp notification
            message_data = {
                'amount_paid': amount,
                'month': defaulter_data['month'],
                'year': defaulter_data['year'],
                'balance_amount': user_data['monthly_fees'] - (
                    existing_payment['amount_paid'] + amount if existing_payment else amount),
                'receipt_number': receipt_number,
                'payment_date': datetime.now().strftime("%Y-%m-%d")
            }
            self.whatsapp_service.send_payment_notification(user_data, message_data)

            popup.dismiss()

            message = f"Payment processed successfully!\nReceipt: {receipt_number}"
            if amount >= defaulter_data['balance_amount']:
                message += "\nUser removed from defaulter list."

            self.show_popup("Success", message)
            self.load_defaulters()  # Refresh the list instantly
        else:
            self.show_popup("Error", f"Failed to process payment: {receipt_number}")

    def send_manual_messages(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        scroll = ScrollView()

        checkboxes_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        checkboxes_layout.bind(minimum_height=checkboxes_layout.setter('height'))

        defaulters = self.db.get_defaulters()
        self.selected_defaulters = []
        # Use a dictionary to track displayed defaulters and avoid duplicates
        displayed_defaulters = {}

        for defaulter in defaulters:
            user = self.db.get_user_by_id(defaulter['user_id'])
            if user and user['status'] == 'Active':
                defaulter_key = f"{user['user_id']}-{defaulter['month']}-{defaulter['year']}"
                if defaulter_key not in displayed_defaulters:
                    displayed_defaulters[defaulter_key] = (defaulter, user)
                    checkbox_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
                    checkbox = CheckBox(size_hint_x=0.2)
                    label = Label(
                        text=f"{user['name']} - {defaulter['month']} {defaulter['year']} - ₹{defaulter['balance_amount']}",
                        halign='left'
                    )

                    checkbox.defaulter_data = defaulter
                    checkbox.user_data = user
                    checkbox.bind(active=self.on_defaulter_selected)

                    checkbox_layout.add_widget(checkbox)
                    checkbox_layout.add_widget(label)
                    checkboxes_layout.add_widget(checkbox_layout)

        scroll.add_widget(checkboxes_layout)
        content.add_widget(scroll)

        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        send_selected_btn = ProfessionalButton(text="Send to Selected")
        send_all_btn = ProfessionalButton(text="Send to All")
        cancel_btn = ProfessionalButton(text="Cancel")

        send_selected_btn.bind(on_press=lambda x: self.send_messages_to_selected(popup))
        send_all_btn.bind(on_press=lambda x: self.send_messages_to_all(popup))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(send_selected_btn)
        btn_layout.add_widget(send_all_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Select Defaulters for Messaging", content=content, size_hint=(0.9, 0.8))
        popup.open()

    def on_defaulter_selected(self, checkbox, value):
        if value:
            self.selected_defaulters.append({
                'defaulter': checkbox.defaulter_data,
                'user': checkbox.user_data
            })
        else:
            self.selected_defaulters = [d for d in self.selected_defaulters
                                        if d['defaulter'] != checkbox.defaulter_data]

    def send_messages_to_selected(self, popup):
        if not self.selected_defaulters:
            self.show_popup("Error", "No defaulters selected")
            return

        success_count = 0
        for item in self.selected_defaulters:
            success = self.whatsapp_service.send_defaulter_reminder(
                item['user'], item['defaulter']
            )
            if success:
                success_count += 1

        popup.dismiss()
        self.show_popup("Success", f"Messages sent to {success_count}/{len(self.selected_defaulters)} defaulters")

    def send_messages_to_all(self, popup):
        defaulters = self.db.get_defaulters()
        success_count = 0
        total_count = 0
        # Use a dictionary to track displayed defaulters and avoid duplicates
        displayed_defaulters = {}

        for defaulter in defaulters:
            user = self.db.get_user_by_id(defaulter['user_id'])
            if user and user['status'] == 'Active':
                defaulter_key = f"{user['user_id']}-{defaulter['month']}-{defaulter['year']}"
                if defaulter_key not in displayed_defaulters:
                    displayed_defaulters[defaulter_key] = (defaulter, user)
                    success = self.whatsapp_service.send_defaulter_reminder(user, defaulter)
                    if success:
                        success_count += 1
                    total_count += 1

        popup.dismiss()
        self.show_popup("Success", f"Messages sent to {success_count}/{total_count} defaulters")

    def schedule_automatic_messages(self):
        # Check if today is 1st, 2nd, 3rd, or 15th of the month
        today = datetime.now()
        if today.day in [1, 2, 3, 15]:
            # Send automatic messages
            Clock.schedule_once(lambda dt: self.send_automatic_messages(), 10)

    def send_automatic_messages(self):
        defaulters = self.db.get_defaulters()
        today = datetime.now()
        # Use a dictionary to track displayed defaulters and avoid duplicates
        displayed_defaulters = {}

        for defaulter in defaulters:
            user = self.db.get_user_by_id(defaulter['user_id'])
            if user and user['status'] == 'Active':
                defaulter_key = f"{user['user_id']}-{defaulter['month']}-{defaulter['year']}"
                if defaulter_key not in displayed_defaulters:
                    displayed_defaulters[defaulter_key] = (defaulter, user)
                    # Customize message based on day of month
                    if today.day == 1:
                        message_type = "first_reminder"
                    elif today.day == 2:
                        message_type = "second_reminder"
                    elif today.day == 3:
                        message_type = "third_reminder"
                    else:  # 15th
                        message_type = "final_reminder"

                    # Send the message
                    self.whatsapp_service.send_defaulter_reminder(user, defaulter, message_type)

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class WhatsAppScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.whatsapp_service = WhatsAppService()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="WhatsApp Notifications", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        # Main content
        main_layout = BoxLayout(orientation='vertical', spacing=20)

        # Send to Defaulters section
        defaulters_section = BoxLayout(orientation='vertical', spacing=10)
        defaulters_section.add_widget(SectionLabel(text="Send to Defaulters"))

        send_all_defaulters_btn = ProfessionalButton(text="Send to All Defaulters")
        send_selected_defaulters_btn = ProfessionalButton(text="Send to Selected Defaulters")

        send_all_defaulters_btn.bind(on_press=self.send_to_all_defaulters)
        send_selected_defaulters_btn.bind(on_press=self.send_to_selected_defaulters)

        defaulters_section.add_widget(send_all_defaulters_btn)
        defaulters_section.add_widget(send_selected_defaulters_btn)

        # Custom Message section
        custom_section = BoxLayout(orientation='vertical', spacing=10)
        custom_section.add_widget(SectionLabel(text="Custom Message"))

        self.custom_message_input = TextInput(
            hint_text="Type your custom message here...",
            size_hint_y=None,
            height='100dp',
            multiline=True
        )
        custom_section.add_widget(self.custom_message_input)

        send_custom_btn = ProfessionalButton(text="Send Custom Message to All")
        send_custom_btn.bind(on_press=self.send_custom_message)
        custom_section.add_widget(send_custom_btn)

        main_layout.add_widget(defaulters_section)
        main_layout.add_widget(custom_section)

        # Info section
        info_label = Label(
            text="Messages will be sent to active users only.\nWhatsApp will open with pre-filled messages.",
            size_hint_y=None,
            height='60dp',
            text_size=(None, None),
            halign='center',
            color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(info_label)

        layout.add_widget(main_layout)
        self.add_widget(layout)

    def refresh_screen(self, instance):
        self.custom_message_input.text = ""
        self.show_popup("Info", "Screen refreshed successfully")

    def send_to_all_defaulters(self, instance):
        defaulters = self.db.get_defaulters()
        success_count = 0
        total_count = 0

        for defaulter in defaulters:
            user = self.db.get_user_by_id(defaulter['user_id'])
            if user and user['status'] == 'Active':
                success = self.whatsapp_service.send_defaulter_reminder(user, defaulter)
                if success:
                    success_count += 1
                total_count += 1

        self.show_popup("Success", f"Messages sent to {success_count}/{total_count} defaulters")

    def send_to_selected_defaulters(self, instance):
        # Reuse the method from DefaulterScreen
        defaulter_screen = self.manager.get_screen('defaulters')
        defaulter_screen.send_manual_messages(instance)

    def send_custom_message(self, instance):
        custom_message = self.custom_message_input.text.strip()
        if not custom_message:
            self.show_popup("Error", "Please enter a custom message")
            return

        users = self.db.get_all_users()
        success_count = 0
        total_count = 0

        for user in users:
            if user['status'] == 'Active':
                success = self.whatsapp_service.send_message(user['mobile_number'], custom_message)
                if success:
                    success_count += 1
                total_count += 1

        self.show_popup("Success", f"Custom message sent to {success_count}/{total_count} users")
        self.custom_message_input.text = ""

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.report_gen = ReportGenerator()
        self.db = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="Reports Generation", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        # Report selection section
        selection_section = GridLayout(cols=2, spacing=10, size_hint_y=0.6)

        # User Reports
        selection_section.add_widget(SectionLabel(text="User Reports"))
        user_reports_layout = BoxLayout(orientation='vertical', spacing=5)

        all_users_btn = ProfessionalButton(text="All Users Report (PDF)")
        user_details_btn = ProfessionalButton(text="User Details with Image (PDF)")

        all_users_btn.bind(on_press=self.generate_all_users_report)
        user_details_btn.bind(on_press=self.generate_user_details_report)

        user_reports_layout.add_widget(all_users_btn)
        user_reports_layout.add_widget(user_details_btn)
        selection_section.add_widget(user_reports_layout)

        # Payment Reports
        selection_section.add_widget(SectionLabel(text="Payment Reports"))
        payment_reports_layout = BoxLayout(orientation='vertical', spacing=5)

        all_payments_btn = ProfessionalButton(text="All Payments Report (PDF)")
        user_payments_btn = ProfessionalButton(text="User Payments with Image (PDF)")

        all_payments_btn.bind(on_press=self.generate_all_payments_report)
        user_payments_btn.bind(on_press=self.generate_user_payments_report)

        payment_reports_layout.add_widget(all_payments_btn)
        payment_reports_layout.add_widget(user_payments_btn)
        selection_section.add_widget(payment_reports_layout)

        layout.add_widget(selection_section)

        # User selection for individual reports
        user_selection_section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.4)
        user_selection_section.add_widget(SectionLabel(text="Select User for Individual Reports"))

        user_search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.user_search_input = ProfessionalTextInput(hint_text="Search user by ID/Name/Aadhar")
        search_btn = ProfessionalButton(text="Search", size_hint_x=0.3)
        search_btn.bind(on_press=self.search_user_for_report)
        user_search_layout.add_widget(self.user_search_input)
        user_search_layout.add_widget(search_btn)
        user_selection_section.add_widget(user_search_layout)

        self.selected_user_label = FormLabel(
            text="No user selected",
            height='40dp'
        )
        user_selection_section.add_widget(self.selected_user_label)

        self.selected_user = None
        layout.add_widget(user_selection_section)

        self.add_widget(layout)

    def refresh_screen(self, instance):
        self.user_search_input.text = ""
        self.selected_user_label.text = "No user selected"
        self.selected_user = None
        self.show_popup("Info", "Screen refreshed successfully")

    def search_user_for_report(self, instance):
        search_term = self.user_search_input.text
        if not search_term:
            self.show_popup("Error", "Please enter search term")
            return

        users = self.db.search_users(search_term)
        if not users:
            self.show_popup("Error", "No user found")
            return

        if len(users) == 1:
            self.select_user_for_report(users[0])
        else:
            self.show_user_selection_for_report(users)

    def show_user_selection_for_report(self, users):
        content = BoxLayout(orientation='vertical', spacing=10)
        scroll = ScrollView()

        user_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        user_list.bind(minimum_height=user_list.setter('height'))

        for user in users:
            btn = ProfessionalButton(
                text=f"ID: {user['user_id']} - {user['name']} - {user['mobile_number']}",
                size_hint_y=None,
                height='40dp'
            )
            btn.user_data = user
            btn.bind(on_press=lambda x: self.select_user_for_report(x.user_data))
            user_list.add_widget(btn)

        scroll.add_widget(user_list)
        content.add_widget(scroll)

        popup = Popup(title="Select User for Report", content=content, size_hint=(0.9, 0.8))
        popup.open()

    def select_user_for_report(self, user):
        self.selected_user = user
        self.selected_user_label.text = f"Selected: {user['name']} (ID: {user['user_id']})"

    def generate_all_users_report(self, instance):
        try:
            users = self.db.get_all_users()
            filename = self.report_gen.generate_all_users_report(users)
            self.show_popup("Success", f"Report generated successfully!\nSaved as: {filename}")
        except Exception as e:
            self.show_popup("Error", f"Failed to generate report: {str(e)}")

    def generate_user_details_report(self, instance):
        if not self.selected_user:
            self.show_popup("Error", "Please select a user first")
            return

        try:
            filename = self.report_gen.generate_user_report(self.selected_user, include_image=True)
            self.show_popup("Success", f"User report generated successfully!\nSaved as: {filename}")
        except Exception as e:
            self.show_popup("Error", f"Failed to generate user report: {str(e)}")

    def generate_all_payments_report(self, instance):
        try:
            # Get all payments data
            all_users = self.db.get_all_users()
            all_payments = []
            for user in all_users:
                user_payments = self.db.get_payments_by_user(user['user_id'])
                for payment in user_payments:
                    payment['user_name'] = user['name']
                    all_payments.append(payment)

            filename = self.report_gen.generate_payments_report(all_payments)
            self.show_popup("Success", f"Payments report generated successfully!\nSaved as: {filename}")
        except Exception as e:
            self.show_popup("Error", f"Failed to generate payments report: {str(e)}")

    def generate_user_payments_report(self, instance):
        if not self.selected_user:
            self.show_popup("Error", "Please select a user first")
            return

        try:
            payments = self.db.get_payments_by_user(self.selected_user['user_id'])
            filename = self.report_gen.generate_user_payments_report(self.selected_user, payments)
            self.show_popup("Success", f"User payments report generated successfully!\nSaved as: {filename}")
        except Exception as e:
            self.show_popup("Error", f"Failed to generate user payments report: {str(e)}")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class SeatChartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="Seat Chart", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        scroll = ScrollView()
        self.seat_grid = GridLayout(cols=10, spacing=5, size_hint_y=None)
        self.seat_grid.bind(minimum_height=self.seat_grid.setter('height'))

        scroll.add_widget(self.seat_grid)
        layout.add_widget(scroll)

        # Legend
        legend_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        legend_layout.add_widget(Label(text="Available: ", size_hint_x=0.3))
        available_indicator = Button(background_color=(0.2, 0.6, 0.8, 1), background_normal='', size_hint_x=0.1)
        legend_layout.add_widget(available_indicator)
        legend_layout.add_widget(Label(text="Booked: ", size_hint_x=0.3))
        booked_indicator = Button(background_color=(0.8, 0.2, 0.2, 1), background_normal='', size_hint_x=0.1)
        legend_layout.add_widget(booked_indicator)
        layout.add_widget(legend_layout)

        self.add_widget(layout)
        self.load_seat_chart()

    def refresh_screen(self, instance):
        self.load_seat_chart()
        self.show_popup("Info", "Seat chart refreshed successfully")

    def load_seat_chart(self):
        self.seat_grid.clear_widgets()

        # Get booked seats
        users = self.db.get_all_users()
        booked_seats = [user['seat_number'] for user in users if user['seat_number']]

        # Create 300 seats
        for i in range(1, 301):
            if i in booked_seats:
                # Find user for this seat
                user = next((u for u in users if u['seat_number'] == i), None)
                seat_text = f"{i}\n{user['name'][:3] if user else 'Booked'}" if i in booked_seats else str(i)
                seat_btn = Button(
                    text=seat_text,
                    size_hint_y=None,
                    height='40dp',
                    background_color=(0.8, 0.2, 0.2, 1) if i in booked_seats else (0.2, 0.6, 0.8, 1),
                    background_normal='',
                    font_size='15sp',
                    font_name = "assets/fonts/NotoSansDevanagari-Regular.ttf"
                )
            else:
                seat_btn = Button(
                    text=str(i),
                    size_hint_y=None,
                    height='40dp',
                    background_color=(0.2, 0.6, 0.8, 1),
                    background_normal=''
                )

            seat_btn.seat_number = i
            seat_btn.bind(on_press=self.on_seat_click)
            self.seat_grid.add_widget(seat_btn)

    def on_seat_click(self, instance):
        seat_number = instance.seat_number
        users = self.db.get_all_users()
        user = next((u for u in users if u['seat_number'] == seat_number), None)

        if user:
            message = f"Seat {seat_number}\nBooked by: {user['name']}\nMobile: {user['mobile_number']}\nStatus: {user['status']}"
        else:
            message = f"Seat {seat_number}\nStatus: Available"

        self.show_popup("Seat Information", message)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()


class BackupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_service = BackupService()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header = HeaderLabel(text="Backup & Restore", size_hint_x=0.8)
        refresh_btn = ProfessionalButton(text="Refresh", size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_screen)
        header_layout.add_widget(header)
        header_layout.add_widget(refresh_btn)
        layout.add_widget(header_layout)

        backup_btn = ProfessionalButton(text="Create Backup")
        restore_btn = ProfessionalButton(text="Restore Backup")

        backup_btn.bind(on_press=self.create_backup)
        restore_btn.bind(on_press=self.restore_backup)

        layout.add_widget(backup_btn)
        layout.add_widget(restore_btn)

        # Info label
        info_label = Label(
            text="Backup creates a copy of the database.\nRestore will replace current data with backup.\nAutomatic backup on 28th of every month.",
            size_hint_y=None,
            height='80dp',
            text_size=(None, None),
            halign='center',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(info_label)

        self.add_widget(layout)

    def refresh_screen(self, instance):
        self.show_popup("Info", "Screen refreshed successfully")

    def create_backup(self, instance):
        success = self.backup_service.create_backup()
        if success:
            self.show_popup("Success", "Backup created successfully")
        else:
            self.show_popup("Error", "Backup failed")

    def restore_backup(self, instance):
        success = self.backup_service.restore_backup()
        if success:
            self.show_popup("Success", "Restore completed successfully")
        else:
            self.show_popup("Error", "Restore failed")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        ok_btn = ProfessionalButton(text='OK', size_hint_y=None, height='40dp')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_btn)
        popup.open()


class SeatChartPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Select Seat"
        self.size_hint = (0.9, 0.8)

        layout = BoxLayout(orientation='vertical')
        scroll = ScrollView()

        seat_grid = GridLayout(cols=10, spacing=5, size_hint_y=None)
        seat_grid.bind(minimum_height=seat_grid.setter('height'))

        # Get booked seats from database
        db = DatabaseManager()
        users = db.get_all_users()
        booked_seats = [user['seat_number'] for user in users if user['seat_number']]

        for i in range(1, 301):
            seat_btn = Button(
                text=str(i),
                size_hint_y=None,
                height='40dp',
                background_color=(0.8, 0.2, 0.2, 1) if i in booked_seats else (0.2, 0.6, 0.8, 1),
                background_normal=''
            )
            if i in booked_seats:
                seat_btn.disabled = True
                seat_btn.text += " (Booked)"

            seat_btn.seat_number = i
            seat_btn.bind(on_press=self.select_seat)
            seat_grid.add_widget(seat_btn)

        scroll.add_widget(seat_grid)
        layout.add_widget(scroll)
        self.content = layout

    def select_seat(self, instance):
        if not instance.disabled:
            self.callback(instance.seat_number)
            self.dismiss()


class GymManagementApp(App):
    def build(self):
        self.title = "Sunil's Mittal Reading Library"

        # Initialize database
        self.db = DatabaseManager()
        self.db.initialize_database()

        # Create screen manager
        self.sm = ScreenManager()

        # Add screens
        screens = [
            ('add_user', UserAddScreen(name='add_user')),
            ('view_users', ViewUsersScreen(name='view_users')),
            ('payments', PaymentScreen(name='payments')),
            ('defaulters', DefaulterScreen(name='defaulters')),
            ('whatsapp', WhatsAppScreen(name='whatsapp')),
            ('reports', ReportsScreen(name='reports')),
            ('seats', SeatChartScreen(name='seats')),
            ('backup', BackupScreen(name='backup'))
        ]

        for name, screen in screens:
            self.sm.add_widget(screen)

        # Create navigation
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')

        nav_buttons = [
            ('Add User', 'add_user'),
            ('View Users', 'view_users'),
            ('Payments', 'payments'),
            ('Defaulters', 'defaulters'),
            ('Reports', 'reports'),
            ('Backup', 'backup')
        ]

        for text, screen_name in nav_buttons:
            btn = ProfessionalButton(text=text, size_hint_x=1, font_size='16sp',font_name = "assets/fonts/NotoSansDevanagari-Regular.ttf")
            btn.bind(on_press=lambda x, name=screen_name: self.switch_screen(name))
            nav_layout.add_widget(btn)

        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.sm)
        main_layout.add_widget(nav_layout)

        return main_layout

    def switch_screen(self, screen_name):
        self.sm.current = screen_name


if __name__ == '__main__':
    GymManagementApp().run()