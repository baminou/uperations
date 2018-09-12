

import os
import shutil
from termcolor import cprint
import tempfile
from contracts import contract
from operations.library import LibraryException, LibraryNotFound
from operation_types.operation import OperationException

@contract(library_name='str', out_dir='str', returns='str')
def library_create(library_name, out_dir):
    """
    Create a new libary

    Args:
        library_name (str): Name of the library to create
        out_dir (str): Path of the directory where the library is going to be created

    Return:
        str: Path of the newly created library
    """

    if library_exists(library_name, out_dir):
        raise LibraryException("The library "+library_name+" already exists under "+out_dir)

    if not os.path.isdir(out_dir):
        raise FileNotFoundError(out_dir+" does not exist")

    library_new_path = os.path.join(out_dir, str(library_name).lower())
    library_new_init = os.path.join(library_new_path, '__init__.py')
    tmp_dir = os.path.join(tempfile.mkdtemp(),'tmp')
    tmp_init = os.path.join(tmp_dir, '__init__.py')

    shutil.copytree(os.path.join('operations','base','utils','templates','make_library'), tmp_dir)
    replace_placeholders_in_file(tmp_init, {'LIBRARYNAME':library_name.lower()})
    shutil.copytree(tmp_dir,library_new_path)
    shutil.rmtree(tmp_dir)

    cprint("Library successfully created under: %s" % library_new_init, 'green')

    return library_new_path

@contract(file_path='str', placeholders='dict')
def replace_placeholders_in_file(file_path, placeholders):
    """
    Replace a dictionary of placeholders in an existing file

    Args:
        file_path (str): Path of the file with the placeholders
        placeholders (dict): Dictionary containing list of placeholders as key, value {PLACEHOLDER: new_value}

    Raises:
        FileNotFoundError: file_path does not exist
        TypeError: file_path is not a string
        TypeError: placeholders is not a dict
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path+" does not exist")

    for key in placeholders:
        with open(file_path, 'r') as f:
            new_text = f.read().replace(key, placeholders[key])

        with open(file_path, 'w') as f:
            f.write(new_text)
    return

@contract(name='str',operations_dir='str', returns='bool')
def library_exists(name, operations_dir):
    """
    Check if a library exists in the specified directory

    Args:
        name: Name of the library to check existence
        operations_dir: Path of the operations directory

    Return:
        bool: True if the library exists, False otherwise

    Raises:
        FileNotFoundError: The operations directory does not exist
    """
    if not os.path.isdir(operations_dir):
        raise FileNotFoundError(operations_dir+" does not exist.")

    library_path = os.path.join(os.getcwd(), operations_dir, name)
    return os.path.isdir(library_path)

@contract(operations_dir="str",library_name="str",operation_name="str", returns="bool")
def operation_exists(operations_dir, library_name, operation_name):
    """
    Check if an operation exists or not

    Args:
        operations_dir (str): The directory where you want to create the operation
        library_name (str): Name of the library where to create the operation
        operation_name (str): Name of the operation to create in snake case

    Return:
        bool: True if operation exists, False otherwise

    Raises:
        FileNotFoundError: operations_dir path does not exist or is not found in the system
        LibraryNotFound: The library requested does not exist
    """
    if not os.path.isdir(operations_dir):
        raise FileNotFoundError(operations_dir)

    if not library_exists(library_name, operations_dir):
        raise LibraryNotFound(os.path.join(operations_dir,library_name))

    return os.path.isfile(os.path.join(operations_dir,library_name,operation_name,'__init__.py'))

@contract(operations_dir="str",library_name="str",operation_name="str", returns="str")
def operation_create(operations_dir, library_name, operation_name):
    """
    Create a new operation

    Args:
        library_name (str): Name of the library
        operations_dir (str): Directory of operations

    Return:
        str: Path of the new operation directory

    Raises:
        OperationException: The operation already exists
    """
    if not library_exists(library_name,operations_dir):
        library_create(library_name, operations_dir)

    if operation_exists(operations_dir, library_name, operation_name):
        raise OperationException(os.path.join(operations_dir,library_name, operation_name)+" already exists.")

    operation_new_path = os.path.join(operations_dir, library_name, operation_name)
    operation_new_init = os.path.join(operation_new_path, '__init__.py')
    tmp_dir = os.path.join(tempfile.mkdtemp(),'tmp')
    tmp_init = os.path.join(tmp_dir, '__init__.py')

    shutil.copytree(os.path.join('operations','base','utils','templates','make_operation'), tmp_dir)
    replace_placeholders_in_file(tmp_init, {'NEWOPERATION':to_camel_case(operation_name)})
    shutil.copytree(tmp_dir,operation_new_path)
    shutil.rmtree(tmp_dir)

    cprint("Operation successfully created under: %s" % operation_new_init, 'green')
    return operation_new_path

@contract(snake_str="str", returns='str')
def to_camel_case(snake_str):
    """
    Convert string from snake case to camel case

    Args:
        snake_str (str): A string in snake case

    Return:
        str: Input string in camel case
    """
    components = snake_str.split('_')
    return components[0].title() + ''.join(x.title() for x in components[1:])