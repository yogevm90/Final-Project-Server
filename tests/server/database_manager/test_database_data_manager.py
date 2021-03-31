import pytest

from tests.server.database_manager import pre_test


@pytest.fixture(scope='session', autouse=True)
def database_manager():
    return pre_test.database_manager()


def test_get_user_by_name(database_manager):
    result = database_manager.get_user_by_name('dani')
    assert result['username'] == 'dani'


def test_get_class_by_name(database_manager):
    result = database_manager.get_class_by_name('class1')
    assert result['name'] == 'class1'


def test_insert_user(database_manager):
    database_manager.insert_user(username='user', password='password', details={'age': 21, 'id': '100000'})
    result = database_manager.get_user_by_name('user')
    assert result['username'] == 'user'


def test_remove_user(database_manager):
    database_manager.remove_user(username='dani')
    result = database_manager.get_user_by_name('dani')
    assert result is None


def test_insert_class_no_participants(database_manager):
    database_manager.insert_class(class_name='some_class', teacher_username='teacher', details={'time': '1830'})
    result = database_manager.get_class_by_name('some_class')
    assert result['name'] == 'some_class' and len(result['participants']) == 0


def test_insert_class_with_participants(database_manager):
    database_manager.insert_class(class_name='some_class1', teacher_username='teacher', details={'time': '1830'},
                                  participants=['moshe'])
    result = database_manager.get_class_by_name('some_class1')
    assert result['name'] == 'some_class1' and result['participants'] == ['moshe']


def test_insert_class_with_none_existing_participants(database_manager):
    with pytest.raises(Exception):
        database_manager.insert_class(class_name='some_class2', teacher_username='teacher', details={'time': '1830'},
                                      participants=['didi'])
        result = database_manager.get_class_by_name('some_class2')


def test_user_exists(database_manager):
    assert database_manager.user_exists('moshe')


def test_class_exists(database_manager):
    assert database_manager.class_exists('class2')


def test_user_participating_class(database_manager):
    assert database_manager.user_participating_class('lily', 'class2')


def test_user_participating_class_false(database_manager):
    assert not database_manager.user_participating_class('dani', 'class2')


def test_add_participant(database_manager):
    assert not database_manager.user_participating_class('moshe', 'class2')
    database_manager.add_participant('moshe', 'class2')
    assert database_manager.user_participating_class('moshe', 'class2')
    assert database_manager.user_participating_class('lily', 'class2')


def test_remove_participant(database_manager):
    assert database_manager.user_participating_class('lola', 'class2')
    database_manager.remove_participant('lola', 'class2')
    assert not database_manager.user_participating_class('lola', 'class2')


def test_is_teacher(database_manager):
    assert database_manager.is_teacher('moshiko', 'class2')


def test_is_teacher_false(database_manager):
    assert not database_manager.is_teacher('moshe', 'class2')


def test_update_user(database_manager):
    user_document = database_manager.get_user_by_name('moshe')
    assert user_document['details']['age'] == 3
    user_document['details']['age'] = 4
    user_document['details']['email'] = 'idanos@walla.co.il'
    database_manager.update_user('moshe', user_document)
    updated_user_document = database_manager.get_user_by_name('moshe')
    assert updated_user_document['details']['age'] == 4
    assert updated_user_document['details']['email'] == 'idanos@walla.co.il'
    assert updated_user_document['password'] == '1234'


def test_update_class(database_manager):
    class_document = database_manager.get_class_by_name('class2')
    assert class_document['details']['date'] == '230321'
    class_document['details']['date'] = '240321'
    class_document['details']['homework'] = 'homework1.pdf'
    database_manager.update_class('class2', class_document)
    updated_class_document = database_manager.get_class_by_name('class2')
    assert updated_class_document['details']['date'] == '240321'
    assert updated_class_document['details']['homework'] == 'homework1.pdf'
    assert updated_class_document['teacher'] == 'moshiko'
