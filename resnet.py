"""ResNet models for Keras.
Reference:
  - [Deep Residual Learning for Image Recognition](
      https://arxiv.org/abs/1512.03385) (CVPR 2015)
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import tensorflow as tf

BASE_WEIGHTS_PATH = (
    'https://storage.googleapis.com/tensorflow/keras-applications/resnet/')

WEIGHTS_HASHES = {
    'resnet50': ('2cb95161c43110f7111970584f804107',
                 '4d473c1dd8becc155b73f8504c6f6626'),
    'resnet101': ('f1aeb4b969a6efcfb50fad2f0c20cfc5',
                  '88cf7a10940856eca736dc7b7e228a21'),
    'resnet152': ('100835be76be38e30d865e96f2aaae62',
                  'ee4c566cf9a93f14d82f913c2dc6dd0c'),
    'resnet50v2': ('3ef43a0b657b3be2300d5770ece849e0',
                   'fac2f116257151a9d068a22e544a4917'),
    'resnet101v2': ('6343647c601c52e1368623803854d971',
                    'c0ed64b8031c3730f411d2eb4eea35b5'),
    'resnet152v2': ('a49b44d1979771252814e80f8ec446f9',
                    'ed17cf2e0169df9d443503ef94b23b33'),
    'resnext50': ('67a5b30d522ed92f75a1f16eef299d1a',
                  '62527c363bdd9ec598bed41947b379fc'),
    'resnext101':
        ('34fb605428fcc7aa4d62f44404c11509', '0f678c91647380debd923963594981b3')
}

def ResNet(stack_fn,
           preact,
           use_bias,
           model_name='resnet',
           include_top=True,
           weights='imagenet',
           input_tensor=None,
           input_shape=None,
           pooling=None,
           classes=1000,
           classifier_activation='softmax',
           **kwargs):
  """
  Instantiates the ResNet, ResNetV2, and ResNeXt architecture.
  Reference:
  - [Deep Residual Learning for Image Recognition](
      https://arxiv.org/abs/1512.03385) (CVPR 2015)
  Optionally loads weights pre-trained on ImageNet.
  Note that the data format convention used by the model is
  the one specified in your Keras config at `~/.keras/keras.json`.
  Caution: Be sure to properly pre-process your inputs to the application.
  Please see `applications.resnet.preprocess_input` for an example.
  Arguments:
    stack_fn: a function that returns output tensor for the stacked residual blocks.
    preact: whether to use pre-activation or not (True for ResNetV2, False for ResNet and ResNeXt).
    use_bias: whether to use biases for convolutional layers or not (True for ResNet and ResNetV2, False for ResNeXt).
    model_name: string, model name.
    include_top: whether to include the fully-connected layer at the top of the network.
    weights: one of `None` (random initialization), 'imagenet' (pre-training on ImageNet), or the path to the weights file to be loaded.
    input_tensor: optional Keras tensor (i.e. output of `layers.Input()`) to use as image input for the model.
    input_shape: optional shape tuple, only to be specified
      if `include_top` is False (otherwise the input shape
      has to be `(224, 224, 3)` (with `channels_last` data format)
      or `(3, 224, 224)` (with `channels_first` data format).
      It should have exactly 3 inputs channels.
    pooling: optional pooling mode for feature extraction
      when `include_top` is `False`.
      - `None` means that the output of the model will be
          the 4D tensor output of the
          last convolutional layer.
      - `avg` means that global average pooling
          will be applied to the output of the
          last convolutional layer, and thus
          the output of the model will be a 2D tensor.
      - `max` means that global max pooling will
          be applied.
    classes: optional number of classes to classify images
      into, only to be specified if `include_top` is True, and
      if no `weights` argument is specified.
    classifier_activation: A `str` or callable. The activation function to use
      on the "top" layer. Ignored unless `include_top=True`. Set
      `classifier_activation=None` to return the logits of the "top" layer.
    **kwargs: For backwards compatibility only.
  
  Returns:
    A `keras.Model` instance.
  
  Raises:
    ValueError: in case of invalid argument for `weights`, or invalid input shape.
    ValueError: if `classifier_activation` is not `softmax` or `None` when using a pretrained top layer.
  """
  
  
  if not (weights in {'imagenet', None}):
    raise ValueError('The `weights` argument should be either '
                     '`None` (random initialization), `imagenet` '
                     '(pre-training on ImageNet), '
                     'or the path to the weights file to be loaded.')

  if weights == 'imagenet' and include_top and classes != 1000:
    raise ValueError('If using `weights` as `"imagenet"` with `include_top`'
                     ' as true, `classes` should be 1000')

  # Determine proper input shape
  input_shape = (224, 224, 3)

  if input_tensor is None:
    img_input = tf.keras.Input(shape=input_shape)
  else:
    if not tf.keras.backend.is_keras_tensor(input_tensor):
      img_input = tf.keras.layers.Input(tensor=input_tensor, shape=input_shape)
    else:
      img_input = input_tensor

  bn_axis = 3 if tf.keras.backend.image_data_format() == 'channels_last' else 1

  x = tf.keras.layers.ZeroPadding2D(padding=((3, 3), (3, 3)), name='conv1_pad')(img_input)
  x = tf.keras.layers.Conv2D(64, 7, strides=2, use_bias=use_bias, name='conv1_conv')(x)

  if not preact:
    x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name='conv1_bn')(x)
    x = tf.keras.layers.Activation('relu', name='conv1_relu')(x)

  x = tf.keras.layers.ZeroPadding2D(padding=((1, 1), (1, 1)), name='pool1_pad')(x)
  x = tf.keras.layers.MaxPooling2D(3, strides=2, name='pool1_pool')(x)
  x = stack_fn(x)

  if preact:
    x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name='post_bn')(x)
    x = tf.keras.layers.Activation('relu', name='post_relu')(x)

  if include_top:
    x = tf.keras.layers.GlobalAveragePooling2D(name='avg_pool')(x)
    x = tf.keras.layers.Dense(classes, activation=classifier_activation, name='predictions')(x)
  
  else:
    if pooling == 'avg':
      x = tf.keras.layers.GlobalAveragePooling2D(name='avg_pool')(x)
    elif pooling == 'max':
      x = tf.keras.layers.GlobalMaxPooling2D(name='max_pool')(x)

  # Ensure that the model takes into account
  # any potential predecessors of `input_tensor`.
  if input_tensor is not None:
    inputs = tf.keras.utils.get_source_inputs(tensor=input_tensor)
  else:
    inputs = img_input

  # Create model.
  model = tf.keras.Model(inputs, x, name=model_name)

  # Load weights.
  if (weights == 'imagenet') and (model_name in WEIGHTS_HASHES):
    if include_top:
      file_name = model_name + '_weights_tf_dim_ordering_tf_kernels.h5'
      file_hash = WEIGHTS_HASHES[model_name][0]
    else:
      file_name = model_name + '_weights_tf_dim_ordering_tf_kernels_notop.h5'
      file_hash = WEIGHTS_HASHES[model_name][1]
    
    weights_path = tf.keras.utils.get_file(
        fname=file_name,
        origin=BASE_WEIGHTS_PATH + file_name,
        cache_subdir='models',
        file_hash=file_hash)
    tf.keras.model.load_weights(weights_path)
  
  elif weights is not None:
    tf.keras.model.load_weights(weights)

  return model


def block1(x, filters, kernel_size=3, stride=1, conv_shortcut=True, name=None):
  """
  A residual block.
  Arguments:
    x: input tensor.
    filters: integer, filters of the bottleneck layer.
    kernel_size: default 3, kernel size of the bottleneck layer.
    stride: default 1, stride of the first layer.
    conv_shortcut: default True, use convolution shortcut if True,
        otherwise identity shortcut.
    name: string, block label.
  Returns:
    Output tensor for the residual block.
  """
  
  bn_axis = 3 if tf.keras.backend.image_data_format() == 'channels_last' else 1

  if conv_shortcut:
    shortcut = tf.keras.layers.Conv2D(4 * filters, 1, strides=stride, name=name + '_0_conv')(x)
    shortcut = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_0_bn')(shortcut)
  else:
    shortcut = x

  x = tf.keras.layers.Conv2D(filters, 1, strides=stride, name=name + '_1_conv')(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_1_bn')(x)
  x = tf.keras.layers.Activation('relu', name=name + '_1_relu')(x)

  x = tf.keras.layers.Conv2D(filters, kernel_size, padding='SAME', name=name + '_2_conv')(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_2_bn')(x)
  x = tf.keras.layers.Activation('relu', name=name + '_2_relu')(x)

  x = tf.keras.layers.Conv2D(4 * filters, 1, name=name + '_3_conv')(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_3_bn')(x)

  x = tf.keras.layers.Add(name=name + '_add')([shortcut, x])
  x = tf.keras.layers.Activation('relu', name=name + '_out')(x)
  
  return x


def block2(x, filters, kernel_size=3, stride=1, conv_shortcut=False, name=None):
  """
  A residual block.
  Arguments:
      x: input tensor.
      filters: integer, filters of the bottleneck layer.
      kernel_size: default 3, kernel size of the bottleneck layer.
      stride: default 1, stride of the first layer.
      conv_shortcut: default False, use convolution shortcut if True,
        otherwise identity shortcut.
      name: string, block label.
  Returns:
    Output tensor for the residual block.
  """

  bn_axis = 3 if backend.image_data_format() == 'channels_last' else 1

  preact = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_preact_bn')(x)
  preact = tf.keras.layers.Activation('relu', name=name + '_preact_relu')(preact)

  if conv_shortcut:
    shortcut = tf.keras.layers.Conv2D(4 * filters, 1, strides=stride, name=name + '_0_conv')(preact)
  else:
    shortcut = tf.keras.layers.MaxPooling2D(1, strides=stride)(x) if stride > 1 else x

  x = tf.keras.layers.Conv2D(filters, 1, strides=1, use_bias=False, name=name + '_1_conv')(preact)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_1_bn')(x)
  x = tf.keras.layers.Activation('relu', name=name + '_1_relu')(x)

  x = tf.keras.layers.ZeroPadding2D(padding=((1, 1), (1, 1)), name=name + '_2_pad')(x)
  x = tf.keras.layers.Conv2D(
      filters,
      kernel_size,
      strides=stride,
      use_bias=False,
      name=name + '_2_conv')(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_2_bn')(x)
  x = tf.keras.layers.Activation('relu', name=name + '_2_relu')(x)

  x = tf.keras.layers.Conv2D(4 * filters, 1, name=name + '_3_conv')(x)
  x = tf.keras.layers.Add(name=name + '_out')([shortcut, x])
  return x


def block3(x,
           filters,
           kernel_size=3,
           stride=1,
           groups=32,
           conv_shortcut=True,
           name=None):
  """
  A residual block.
  Arguments:
    x: input tensor.
    filters: integer, filters of the bottleneck layer.
    kernel_size: default 3, kernel size of the bottleneck layer.
    stride: default 1, stride of the first layer.
    groups: default 32, group size for grouped convolution.
    conv_shortcut: default True, use convolution shortcut if True,
        otherwise identity shortcut.
    name: string, block label.
  Returns:
    Output tensor for the residual block.
  """
  bn_axis = 3 if tf.keras.backend.image_data_format() == 'channels_last' else 1

  if conv_shortcut:
    shortcut = tf.keras.layers.Conv2D(
        (64 // groups) * filters,
        1,
        strides=stride,
        use_bias=False,
        name=name + '_0_conv')(x)
    shortcut = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_0_bn')(shortcut)
  else:
    shortcut = x

  x = tf.keras.layers.Conv2D(filters, 1, use_bias=False, name=name + '_1_conv')(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_1_bn')(x)
  x = tf.keras.layers.Activation('relu', name=name + '_1_relu')(x)

  c = filters // groups
  x = tf.keras.layers.ZeroPadding2D(padding=((1, 1), (1, 1)), name=name + '_2_pad')(x)
  x = tf.keras.layers.DepthwiseConv2D(
      kernel_size,
      strides=stride,
      depth_multiplier=c,
      use_bias=False,
      name=name + '_2_conv')(x)
  x_shape = tf.keras.backend.int_shape(x)[1:-1]
  x = tf.keras.layers.Reshape(x_shape + (groups, c, c))(x)
  x = tf.keras.layers.Lambda(
      lambda x: sum(x[:, :, :, :, i] for i in range(c)),
      name=name + '_2_reduce')(x)
  x = tf.keras.layers.Reshape(x_shape + (filters,))(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_2_bn')(x)
  x = tf.keras.layers.Activation('relu', name=name + '_2_relu')(x)

  x = tf.keras.layers.Conv2D(
      (64 // groups) * filters, 1, use_bias=False, name=name + '_3_conv')(x)
  x = tf.keras.layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_3_bn')(x)

  x = tf.keras.layers.Add(name=name + '_add')([shortcut, x])
  x = tf.keras.layers.Activation('relu', name=name + '_out')(x)
  
  return x


def stack1(x, filters, blocks, stride1=2, name=None):
  """A set of stacked residual blocks.
  Arguments:
    x: input tensor.
    filters: integer, filters of the bottleneck layer in a block.
    blocks: integer, blocks in the stacked blocks.
    stride1: default 2, stride of the first layer in the first block.
    name: string, stack label.
  Returns:
    Output tensor for the stacked blocks.
  """
  x = block1(x, filters, stride=stride1, name=name + '_block1')
  for i in range(2, blocks + 1):
    x = block1(x, filters, conv_shortcut=False, name=name + '_block' + str(i))
  return x



def stack2(x, filters, blocks, stride1=2, name=None):
  """
  A set of stacked residual blocks.
  Arguments:
      x: input tensor.
      filters: integer, filters of the bottleneck layer in a block.
      blocks: integer, blocks in the stacked blocks.
      stride1: default 2, stride of the first layer in the first block.
      name: string, stack label.
  Returns:
      Output tensor for the stacked blocks.
  """
  x = block2(x, filters, conv_shortcut=True, name=name + '_block1')
  for i in range(2, blocks):
    x = block2(x, filters, name=name + '_block' + str(i))
  x = block2(x, filters, stride=stride1, name=name + '_block' + str(blocks))
  return x



def stack3(x, filters, blocks, stride1=2, groups=32, name=None):
  """
  A set of stacked residual blocks.
  Arguments:
    x: input tensor.
    filters: integer, filters of the bottleneck layer in a block.
    blocks: integer, blocks in the stacked blocks.
    stride1: default 2, stride of the first layer in the first block.
    groups: default 32, group size for grouped convolution.
    name: string, stack label.
  Returns:
    Output tensor for the stacked blocks.
  """
  x = block3(x, filters, stride=stride1, groups=groups, name=name + '_block1')
  for i in range(2, blocks + 1):
    x = block3(
        x,
        filters,
        groups=groups,
        conv_shortcut=False,
        name=name + '_block' + str(i))
  return x



def ResNet50(include_top=True,
             weights='imagenet',
             input_tensor=None,
             input_shape=None,
             pooling=None,
             classes=1000,
             **kwargs):
  """
  Instantiates the ResNet50 architecture.
  """

  def stack_fn(x):
    x = stack1(x, 64, 3, stride1=1, name='conv2')
    x = stack1(x, 128, 4, name='conv3')
    x = stack1(x, 256, 6, name='conv4')
    return stack1(x, 512, 3, name='conv5')

  return ResNet(stack_fn, False, True, 'resnet50', include_top, weights,
                input_tensor, input_shape, pooling, classes, **kwargs)