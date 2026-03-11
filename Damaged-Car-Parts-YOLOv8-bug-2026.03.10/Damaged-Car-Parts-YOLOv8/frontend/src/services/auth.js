// 认证服务

// 模拟用户数据
const users = [
  {
    id: 1,
    username: 'admin',
    password: '123456',
    name: '管理员'
  }
];

// 存储用户信息到本地存储
const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

// 从本地存储获取用户信息
const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// 清除本地存储的用户信息
const clearUser = () => {
  localStorage.removeItem('user');
};

// 登录
const login = (username, password) => {
  const user = users.find(u => u.username === username && u.password === password);
  if (user) {
    setUser(user);
    return { success: true, user };
  }
  return { success: false, message: '用户名或密码错误' };
};

// 注册
const register = (username, password, name) => {
  const existingUser = users.find(u => u.username === username);
  if (existingUser) {
    return { success: false, message: '用户名已存在' };
  }
  
  const newUser = {
    id: users.length + 1,
    username,
    password,
    name
  };
  
  users.push(newUser);
  setUser(newUser);
  return { success: true, user: newUser };
};

// 退出登录
const logout = () => {
  clearUser();
};

// 检查是否已登录
const isLoggedIn = () => {
  return !!getUser();
};

export default {
  login,
  register,
  logout,
  isLoggedIn,
  getUser
};