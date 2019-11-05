import * as React from 'react';

import { ReactWidget } from '@jupyterlab/apputils';

import {
  IZenodoRegistry,
  ZenodoFormFields,
  ZenodoConfig,
  ZenodoRecord
} from './tokens';

namespace ZenodoFormInput {
  export interface IProps {
    readonly id: string;
    readonly label: string;
    readonly required: boolean;
    readonly multiline: boolean;
    readonly default?: string;
  }
}

export class ZenodoFormInput extends React.Component<
  ZenodoFormInput.IProps,
  {}
> {
  constructor(props: ZenodoFormInput.IProps) {
    super(props);
    this.id = `zenInput-${this.props.id}`;
  }

  render() {
    const classNames = ['label'];

    if (this.props.required) {
      classNames.push('required');
    }

    return (
      <div className="zenodo-InputRow">
        <label htmlFor={this.id} className={classNames.join(' ')}>
          {this.props.label}
        </label>
        {this.props.multiline ? (
          <textarea
            id={this.id}
            name={this.props.id}
            required={this.props.required}
            rows={5}
          >
            {this.props.default}
          </textarea>
        ) : (
          <input
            id={this.id}
            name={this.props.id}
            required={this.props.required}
            type="text"
            value={this.props.default}
          />
        )}
      </div>
    );
  }

  private id: string;

  static defaultProps: ZenodoFormInput.IProps = {
    label: '',
    id: '',
    required: false,
    multiline: false
  };
}

namespace ZenodoUploadForm {
  export interface IProps {
    readonly onSubmit: React.FormEventHandler;
    readonly defaults: ZenodoFormFields;
  }

  export interface IState {
    error?: string;
  }
}

export class ZenodoUploadForm extends React.Component<
  ZenodoUploadForm.IProps,
  ZenodoUploadForm.IState
> {
  constructor(props: ZenodoUploadForm.IProps) {
    super(props);
    this.state = {
      error: null
    };
  }

  render() {
    return (
      <form id='submit-form' onSubmit={this.props.onSubmit}>
        <h2>Final Submission Details</h2>
        <p>
          Please fill out the required fields and then click 'Publish' to
          publish to Zenodo.
        </p>
        <p>
          <em>Note:</em> this will make your code publicly accessible on{' '}
          <a href='https://zenodo.org'>zenodo.org</a>.
        </p>
        <div id='form-error-div'>{this.state.error}</div>
        <ZenodoFormInput
          id='title'
          label='Title'
          required
          default={this.props.defaults.title}
        />
        <ZenodoFormInput
          id='author'
          label='Author(s)'
          required
          default={this.props.defaults.author}
        />
        <ZenodoFormInput
          id='affiliation'
          label='Affiliation'
          required
          default={this.props.defaults.affiliation}
        />
        <ZenodoFormInput
          id='description'
          label='Description'
          default={this.props.defaults.description}
          required
          multiline
        />
        <ZenodoFormInput
          id='directory'
          label='Directory to publish'
          default={this.props.defaults.directory}
        />
        <ZenodoFormInput
          id='zenodo_token'
          label='Zenodo access token'
          default={this.props.defaults.zenodoToken}
        />
        <button
          type='submit'
          className='zenodo-PublishButton jp-mod-styled jp-mod-accept'
        >
          Publish
        </button>
      </form>
    );
  }
}

namespace ZenodoSuccessMessage {
  export interface IProps {
    doi: string;
    baseUrl: string;
  }
}

export class ZenodoSuccessMessage extends React.Component<
  ZenodoSuccessMessage.IProps,
  {}
> {
  constructor(props: ZenodoSuccessMessage.IProps) {
    super(props);
    this.onViewButtonClick = this.onViewButtonClick.bind(this);
  }

  get recordUrl() {
    const record = this.props.doi.split('.').pop();
    return `${this.props.baseUrl}/record/${record}`;
  }

  onViewButtonClick(event: React.MouseEvent<HTMLButtonElement, MouseEvent>) {
    event.preventDefault();
    window.open(this.recordUrl, '_blank');
  }

  render() {
    if (!this.props.doi) {
      return <></>;
    }

    return (
      <div>
        <h2>Congratulations, your files have been uploaded to Zenodo!</h2>
        <div>
          <button
            onClick={this.onViewButtonClick}
            className='jp-mod-styled jp-mod-accept'
          >
            View on Zenodo
          </button>
          <strong>{this.props.doi}</strong>
        </div>
        <h3>How is my code shared?</h3>
        <p>
          Your code is now publicly accessible as an archive on{' '}
          <a href={this.recordUrl} target="_blank">
            Zenodo
          </a>{' '}
          . It has been assigned a DOI (digital object identifier):{' '}
          {this.props.doi}.
        </p>
        <h3>What if my code changes?</h3>
        <p>
          If you make changes to your files, you can create a new version on
          Zenodo (which will be linked to the first) by clicking 'Update Zenodo
          Deposition' in the share menu.
        </p>
      </div>
    );
  }
}

namespace ZenodoManager {
  export interface IProps {
    zenodoRegistry: IZenodoRegistry;
    zenodoConfig: ZenodoConfig;
    formDefaults: ZenodoFormFields;
  }

  export type IStateValue = 'waiting' | 'success' | 'error' | 'form';

  export interface IState {
    currentState: IStateValue;
    doi?: string;
    errorMessage?: string;
  }
}

export class ZenodoManager extends React.Component<
  ZenodoManager.IProps,
  ZenodoManager.IState
> {
  constructor(props: ZenodoManager.IProps) {
    super(props);

    this.state = {
      currentState: 'form',
      doi: null,
      errorMessage: null
    };

    this.onSubmit = this.onSubmit.bind(this);
    this.onSuccess = this.onSuccess.bind(this);
    this.onError = this.onError.bind(this);
  }

  onSubmit(event: React.FormEvent) {
    const form = event.target as HTMLFormElement;

    event.preventDefault();

    // Convert form data to JSON
    const formData = new FormData(form);
    const zenodoPost: ZenodoFormFields = {
      title: formData.get('title') as string,
      author: formData.get('author') as string,
      affiliation: formData.get('affiliation') as string,
      description: formData.get('description') as string,
      directory: formData.get('directory') as string,
      zenodoToken: formData.get('zenodo_token') as string
    };

    // Send a POST request with data
    this.setState({ currentState: 'waiting' });
    this.props.zenodoRegistry
      .createDeposition(zenodoPost.directory || '/', zenodoPost)
      .then(this.onSuccess)
      .catch(this.onError);
  }

  render() {
    const hidden = { display: 'none' };
    const block = { display: 'block' };
    const visibilities = this._allStates.reduce(
      (memo, state: ZenodoManager.IStateValue) => {
        memo[state] = this.state.currentState === state ? block : hidden;
        return memo;
      },
      {} as { [key in ZenodoManager.IStateValue]: { display: string } }
    );

    return (
      <div className='zenodo-Upload'>
        <div className='zenodo-WaitMessage' style={visibilities.waiting}>
          Please wait; your files are being uploaded&hellip;
        </div>
        <div className='zenodo-SuccessMessage' style={visibilities.success}>
          <ZenodoSuccessMessage
            baseUrl={this.props.zenodoConfig.baseUrl}
            doi={this.state.doi}
          />
        </div>
        <div className='zenodo-ErrorMessage' style={visibilities.error}>
          {this.state.errorMessage}
        </div>
        <div style={visibilities.form}>
          <ZenodoUploadForm
            onSubmit={this.onSubmit}
            defaults={this.props.formDefaults}
          />
        </div>
      </div>
    );
  }

  private onSuccess(record: ZenodoRecord) {
    this.setState({ currentState: 'success', doi: record.doi });
  }

  private onError(error: Error) {
    this.setState({
      currentState: 'error',
      errorMessage: error.message
    });
  }

  // TODO: is there a way to have TS actually check that this
  // encompasses all the states?
  private _allStates = ['waiting', 'success', 'error', 'form'];
}

export class ZenodoWidget extends ReactWidget {
  constructor(
    zenodoRegistry: IZenodoRegistry,
    zenodoConfig: ZenodoConfig,
    formDefaults: ZenodoFormFields
  ) {
    super();
    this.id = 'zenodo-Widget';
    this._zenodoRegistry = zenodoRegistry;
    this._zenodoConfig = zenodoConfig;
    this._formDefaults = formDefaults;
  }

  render() {
    return (
      <ZenodoManager
        zenodoRegistry={this._zenodoRegistry}
        zenodoConfig={this._zenodoConfig}
        formDefaults={this._formDefaults}
      />
    );
  }

  private _zenodoRegistry: IZenodoRegistry;
  private _zenodoConfig: ZenodoConfig;
  private _formDefaults: ZenodoFormFields;
}
