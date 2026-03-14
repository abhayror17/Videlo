export default {
  // Sidebar Navigation
  nav: {
    generate: '生成',
    text2img: '文生图',
    imgedit: '图片编辑',
    txt2video: '文生视频',
    img2video: '图生视频',
    ads: 'AI广告生成器',
    library: '素材库',
    gallery: '作品集',
    workflow: '工作流构建器',
    credits: '积分'
  },
  
  // Header
  header: {
    home: '首页',
    settings: '设置'
  },
  
  // Settings Panel
  settings: {
    form: '表单',
    json: 'JSON',
    model: '模型',
    imageModels: '图像模型',
    videoModels: '视频模型',
    imageEditModels: '图像编辑模型',
    dimensions: '尺寸',
    steps: '步数',
    fast: '快速',
    quality: '质量',
    fixedAtFlux: 'Flux 2 固定为 4',
    guidanceScale: '引导比例',
    seed: '种子',
    random: '随机',
    duration: '时长',
    fps: '帧率',
    second: '秒',
    seconds: '秒',
    aspectRatio: '宽高比',
    numImages: '图片数量',
    bringYourOwnKey: '自带密钥',
    byokDesc: '使用您自己的 deAPI 密钥访问 AI 模型。获取密钥请访问',
    enterApiKey: '输入您的 deAPI 密钥',
    customKeyActive: '自定义 API 密钥已激活',
    clearKey: '清除密钥',
    saveKey: '保存密钥'
  },
  
  // Home / Generation
  home: {
    clickToUpload: '点击上传图片',
    orSelectFromRecent: '或从下方最近作品中选择',
    yourCreationWillAppear: '您的作品将显示在这里',
    describeImage: '描述您想要生成的图片...',
    describeVideo: '描述您想要生成的视频...',
    describeTransformation: '描述您想要的变换效果...',
    generate: '生成',
    generating: '生成中...',
    recent: '最近',
    enhancePrompt: 'AI增强提示词',
    getRandomPrompt: '获取随机提示词',
    createVideoFromImage: '从图片创建视频',
    describeVideoAnimation: '描述视频动画效果...',
    generateVideo: '生成视频',
    creating: '创建中...',
    pleaseUploadImage: '请上传图片或从最近作品中选择',
    pleaseSelectImage: '请选择图片',
    failedToGenerate: '生成失败，请重试',
    failedToGenerateVideo: '视频生成失败'
  },
  
  // Image Edit
  imageEdit: {
    clickToUpload: '点击上传图片',
    orSelectFromRecent: '或从下方最近编辑中选择',
    describeTransformation: '描述您想要的变换效果... 例如：\'将背景改为日落\'，\'使其看起来像一幅画\'',
    imageLoaded: '图片已加载',
    editImage: '编辑图片',
    editing: '编辑中...',
    recentEdits: '最近编辑',
    failedToEdit: '图片编辑失败，请重试',
    pleaseSelectImage: '请选择图片文件'
  },
  
  // Ad Generator
  ads: {
    yourAdCampaignWillAppear: '您的广告活动将显示在这里',
    enhance: '增强',
    script: '脚本',
    image: '图片',
    video: '视频',
    qa: '质检',
    enhancingConcept: '正在增强您的创意...',
    adScript: '广告脚本',
    generatingBrandImage: '正在生成品牌图片...',
    generatingVideoAd: '正在生成视频广告...',
    mayTakeFewMinutes: '这可能需要几分钟',
    runningQA: '正在进行质检分析...',
    campaignComplete: '广告活动完成！',
    downloadVideo: '下载视频',
    describeAdConcept: '描述您的广告创意... 例如："一款面向年轻职场人士的清爽能量饮料"',
    brandName: '品牌名称（可选）',
    newCampaign: '新活动',
    generateAd: '生成广告',
    starting: '启动中...',
    processing: '处理中...',
    previousCampaigns: '历史活动',
    noBrand: '无品牌',
    failedToStartCampaign: '启动活动失败，请重试'
  },
  
  // Gallery
  gallery: {
    title: '作品集',
    all: '全部',
    images: '图片',
    videos: '视频',
    loading: '加载中...',
    noCreationsYet: '暂无作品',
    startGenerating: '开始创作，您的作品将显示在这里'
  },
  
  // Image Card
  imageCard: {
    generating: '生成中',
    noPreview: '无预览'
  },
  
  // Image Modal
  imageModal: {
    download: '下载',
    mediaNotAvailable: '媒体不可用'
  },
  
  // Common
  common: {
    view: '查看',
    download: '下载',
    createVideo: '创建视频',
    useImage: '使用图片'
  },
  
  // Language
  language: {
    en: 'English',
    zh: '中文'
  },
  
  // Credits
  credits: {
    credits: '积分',
    balance: '积分余额',
    estimated: '预计',
    estimate: '预计积分',
    insufficient: '积分不足',
    purchase: '购买积分',
    addDemo: '添加演示积分',
    videoHint: '更高分辨率和更长的视频消耗更多积分'
  },
  
  // Workflow Builder
  workflow: {
    title: '工作流构建器',
    textPrompt: '文本提示',
    textToImage: '文生图',
    textToVideo: '文生视频',
    imageEdit: '图片编辑',
    imageToVideo: '图生视频',
    textToSpeech: '文本转语音',
    imageAnalysis: '图像分析',
    imageInput: '图片输入',
    bgRemoval: '背景移除',
    videoToText: '视频转文本',
    imageEnhance: '图片增强',
    output: '输出',
    enterPrompt: '输入您的提示词...',
    describeEdit: '描述编辑效果...',
    editPrompt: '编辑提示',
    connectInput: '连接输入',
    clear: '清空',
    run: '运行',
    running: '运行中...',
    preparing: '准备工作流...',
    processing: '处理中...',
    completed: '工作流完成！',
    executionFailed: '工作流执行失败',
    timeout: '工作流执行超时',
    model: '模型',
    language: '语言',
    outputFormat: '输出格式',
    extractedText: '提取的文本',
    deleteNode: '删除节点',
    duplicateNode: '复制节点',
    copy: '复制',
    myWorkflows: '我的工作流',
    saveWorkflow: '保存',
    saveWorkflowTitle: '保存工作流',
    workflowName: '工作流名称',
    enterName: '请输入工作流名称',
    addNodesFirst: '请先添加节点',
    savedSuccess: '工作流保存成功！',
    savedError: '保存工作流失败',
    loadError: '加载工作流失败',
    confirmDelete: '确定要删除此工作流吗？',
    deleteError: '删除工作流失败',
    noSavedWorkflows: '暂无保存的工作流',
    loadWorkflow: '加载',
    deleteWorkflow: '删除',
    cancel: '取消',
    nodes: '节点',
    connections: '连接',
    startBuilding: '开始构建',
    dragNodesHint: '点击或拖拽侧边栏中的节点开始',
    searchNodes: '搜索节点...',
    sectionInput: '输入',
    sectionGenerate: '生成',
    sectionTransform: '转换',
    sectionOutput: '输出',
    save: '保存',
    // New shortcuts and features
    undo: '撤销',
    redo: '重做',
    cutConnection: '切断连接',
    deleteConnection: '删除连接',
    keyboardShortcuts: '键盘快捷键',
    shortcutsGuide: '操作指南',
    gettingStarted: '快速入门',
    infiniteZoom: '无限缩放',
    rightClickMenu: '右键菜单',
    dragToConnect: '拖拽连接',
    selectToCut: '选择后点击切断',
    addNode: '添加节点',
    quickStart: '快速开始',
    settings: '设置',
    zoom: '缩放',
    pan: '平移',
    // Empty state guide
    scrollToZoom: '滚动缩放',
    rightClickForMenu: '右键打开菜单',
    ctrlZToUndo: 'Ctrl+Z 撤销',
    settingsForKey: '设置中添加密钥',
    dragToConnectNodes: '拖拽连接节点',
    selectAndClickX: '选择后点击 ✕ 切断'
  }
}
